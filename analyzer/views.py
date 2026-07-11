from django.shortcuts import get_object_or_404, redirect, render

from .forms import ResumeUploadForm
from .models import ResumeUpload
from .services import analyze_resume_text, extract_resume_text


def home(request):
    return render(request, 'analyzer/home.html')


def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.original_filename = request.FILES['file'].name
            resume.save()
            _analyze_and_save(resume)
            return redirect('analysis_result', pk=resume.pk)
    else:
        form = ResumeUploadForm()

    return render(request, 'analyzer/upload.html', {'form': form})


def analysis_result(request, pk):
    resume = get_object_or_404(ResumeUpload, pk=pk)
    if not resume.score or resume.word_count > 20000:
        _analyze_and_save(resume)
    return render(request, 'analyzer/result.html', {'resume': resume})


def _analyze_and_save(resume):
    text = extract_resume_text(resume.file)
    analysis = analyze_resume_text(text)

    resume.extracted_text = text
    resume.score = analysis['score']
    resume.found_skills = analysis['found_skills']
    resume.found_sections = analysis['found_sections']
    resume.missing_sections = analysis['missing_sections']
    resume.suggestions = analysis['suggestions']
    resume.word_count = analysis['word_count']
    resume.has_email = analysis['has_email']
    resume.has_phone = analysis['has_phone']
    resume.save(update_fields=[
        'extracted_text', 'score', 'found_skills', 'found_sections',
        'missing_sections', 'suggestions', 'word_count', 'has_email', 'has_phone'
    ])

