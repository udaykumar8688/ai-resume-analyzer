from pathlib import Path

from django import forms

from .models import ResumeUpload


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = ResumeUpload
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'accept': '.pdf,.doc,.docx',
            })
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']
        extension = Path(uploaded_file.name).suffix.lower()
        allowed_extensions = {'.pdf', '.doc', '.docx'}

        if extension not in allowed_extensions:
            raise forms.ValidationError('Upload a PDF, DOC, or DOCX file.')

        max_size_mb = 5
        if uploaded_file.size > max_size_mb * 1024 * 1024:
            raise forms.ValidationError(f'File size must be under {max_size_mb} MB.')

        return uploaded_file
