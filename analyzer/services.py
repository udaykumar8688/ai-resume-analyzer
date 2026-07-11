import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

try:
    from pypdf import PdfReader
except ImportError:  # Keeps tests/imports working if dependencies are not installed yet.
    PdfReader = None

SKILLS = [
    'python', 'django', 'flask', 'fastapi', 'javascript', 'typescript', 'react',
    'node', 'html', 'css', 'sql', 'mysql', 'postgresql', 'mongodb', 'git',
    'github', 'docker', 'aws', 'azure', 'java', 'c++', 'c#', 'machine learning',
    'data analysis', 'excel', 'power bi', 'tableau', 'communication', 'leadership',
]

IMPORTANT_SECTIONS = [
    'experience', 'education', 'skills', 'projects', 'certifications', 'summary',
]


def extract_resume_text(file_field):
    file_path = Path(file_field.path)
    extension = file_path.suffix.lower()

    if extension == '.docx':
        return _extract_docx_text(file_path)
    if extension == '.pdf':
        return _extract_pdf_text(file_path)
    if extension == '.doc':
        return ''

    return ''


def analyze_resume_text(text):
    if not text.strip():
        return {
            'score': 0,
            'found_skills': [],
            'found_sections': [],
            'missing_sections': IMPORTANT_SECTIONS,
            'suggestions': [
                'Could not read text from this file. Try uploading a text-based DOCX or PDF resume.',
                'Scanned image PDFs need OCR support, which can be added next.',
            ],
            'word_count': 0,
            'has_email': False,
            'has_phone': False,
        }

    normalized_text = _normalize(text)
    found_skills = _find_terms(normalized_text, SKILLS)
    found_sections = _find_terms(normalized_text, IMPORTANT_SECTIONS)
    missing_sections = [section for section in IMPORTANT_SECTIONS if section not in found_sections]

    has_email = bool(re.search(r'\b[\w.+-]+@[\w.-]+\.\w+\b', text))
    has_phone = bool(re.search(r'(?:\+?\d[\d\s().-]{7,}\d)', text))
    word_count = len(re.findall(r'\b\w+\b', text))

    score = 25
    score += min(len(found_skills) * 5, 30)
    score += len(found_sections) * 5
    score += 10 if has_email else 0
    score += 10 if has_phone else 0
    score += 10 if word_count >= 250 else 0
    score = min(score, 100)

    suggestions = []
    if not has_email or not has_phone:
        suggestions.append('Add clear contact details, including email and phone number.')
    if len(found_skills) < 5:
        suggestions.append('Add more role-specific skills so ATS systems can match your resume better.')
    if missing_sections:
        suggestions.append('Add missing sections: ' + ', '.join(missing_sections) + '.')
    if word_count < 250:
        suggestions.append('Add more detail about projects, experience, tools, and measurable achievements.')
    if not suggestions:
        suggestions.append('Good structure. Next, tailor keywords to the exact job description.')

    return {
        'score': score,
        'found_skills': found_skills,
        'found_sections': found_sections,
        'missing_sections': missing_sections,
        'suggestions': suggestions,
        'word_count': word_count,
        'has_email': has_email,
        'has_phone': has_phone,
    }


def _extract_docx_text(file_path):
    try:
        with zipfile.ZipFile(file_path) as docx:
            xml = docx.read('word/document.xml')
    except (KeyError, zipfile.BadZipFile, FileNotFoundError):
        return ''

    root = ElementTree.fromstring(xml)
    namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    parts = [node.text for node in root.findall('.//w:t', namespace) if node.text]
    return _clean_text(' '.join(parts))


def _extract_pdf_text(file_path):
    text = _extract_pdf_text_with_pypdf(file_path)
    if text:
        return text

    return _extract_pdf_text_fallback(file_path)


def _extract_pdf_text_with_pypdf(file_path):
    if PdfReader is None:
        return ''

    try:
        reader = PdfReader(str(file_path))
    except Exception:
        return ''

    chunks = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ''
        except Exception:
            page_text = ''
        if page_text:
            chunks.append(page_text)

    return _clean_text(' '.join(chunks))


def _extract_pdf_text_fallback(file_path):
    try:
        raw = file_path.read_bytes()
    except FileNotFoundError:
        return ''

    decoded = raw.decode('latin-1', errors='ignore')
    matches = re.findall(r'\(([^()]*)\)\s*Tj|\[(.*?)\]\s*TJ', decoded, flags=re.DOTALL)
    chunks = []

    for simple_text, array_text in matches:
        value = simple_text or array_text
        value = re.sub(r'\\[()\\]', '', value)
        value = re.sub(r'<[0-9A-Fa-f]+>', ' ', value)
        chunks.append(value)

    if not chunks:
        return ''

    extracted = _clean_text(' '.join(chunks))
    if len(re.findall(r'\b\w+\b', extracted)) > 20000:
        return ''

    return extracted


def _clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()


def _find_terms(normalized_text, terms):
    return [term for term in terms if term in normalized_text]


def _normalize(text):
    return re.sub(r'\s+', ' ', text.lower())
