import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from pypdf import PdfWriter

from .models import ResumeUpload
from .services import analyze_resume_text, extract_resume_text


class ResumeUploadTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_upload_page_loads(self):
        response = self.client.get(reverse('upload_resume'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload Resume')

    def test_valid_resume_upload_is_saved_and_analyzed(self):
        uploaded_file = SimpleUploadedFile(
            'resume.pdf',
            b'(Python Django SQL Experience Education Skills Projects test@example.com 9876543210) Tj',
            content_type='application/pdf',
        )

        response = self.client.post(reverse('upload_resume'), {'file': uploaded_file})

        resume = ResumeUpload.objects.get()
        self.assertRedirects(response, reverse('analysis_result', kwargs={'pk': resume.pk}))
        self.assertEqual(resume.original_filename, 'resume.pdf')
        self.assertIn('python', resume.found_skills)
        self.assertGreater(resume.score, 25)

    def test_invalid_file_extension_is_rejected(self):
        uploaded_file = SimpleUploadedFile(
            'notes.txt',
            b'not a resume document',
            content_type='text/plain',
        )

        response = self.client.post(reverse('upload_resume'), {'file': uploaded_file})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ResumeUpload.objects.count(), 0)
        self.assertContains(response, 'Upload a PDF, DOC, or DOCX file.')

    def test_resume_text_analysis_detects_contact_and_sections(self):
        analysis = analyze_resume_text(
            'Email test@example.com phone 9876543210 skills Python Django SQL '
            'experience projects education certifications summary'
        )

        self.assertTrue(analysis['has_email'])
        self.assertTrue(analysis['has_phone'])
        self.assertIn('python', analysis['found_skills'])
        self.assertIn('experience', analysis['found_sections'])
        self.assertEqual(analysis['missing_sections'], [])

    def test_unreadable_pdf_returns_zero_score_guidance(self):
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        file_path = f'{self.media_root}/blank.pdf'
        with open(file_path, 'wb') as pdf_file:
            writer.write(pdf_file)

        resume = ResumeUpload.objects.create(file='blank.pdf', original_filename='blank.pdf')
        text = extract_resume_text(resume.file)
        analysis = analyze_resume_text(text)

        self.assertEqual(text, '')
        self.assertEqual(analysis['score'], 0)
        self.assertEqual(analysis['word_count'], 0)
        self.assertIn('OCR support', analysis['suggestions'][1])
