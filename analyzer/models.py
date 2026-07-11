from django.db import models


class ResumeUpload(models.Model):
    file = models.FileField(upload_to='resumes/')
    original_filename = models.CharField(max_length=255, blank=True)
    extracted_text = models.TextField(blank=True)
    score = models.PositiveSmallIntegerField(default=0)
    found_skills = models.JSONField(default=list, blank=True)
    found_sections = models.JSONField(default=list, blank=True)
    missing_sections = models.JSONField(default=list, blank=True)
    suggestions = models.JSONField(default=list, blank=True)
    word_count = models.PositiveIntegerField(default=0)
    has_email = models.BooleanField(default=False)
    has_phone = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_filename or self.file.name
