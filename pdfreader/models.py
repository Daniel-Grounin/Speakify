from django.db import models

class PDFFile(models.Model):
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='speech/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    text = models.TextField(null=True, blank=True)  # Add this field back

    def __str__(self):
        return self.file.name
