from django.contrib import admin

from .models import ResumeUpload


@admin.register(ResumeUpload)
class ResumeUploadAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'score', 'uploaded_at')
    search_fields = ('original_filename', 'extracted_text')
    readonly_fields = ('uploaded_at',)
