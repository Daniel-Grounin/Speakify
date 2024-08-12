import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from gtts import gTTS
import fitz  # PyMuPDF
from PIL import Image
import io
from django.core.files import File
from .forms import PDFFileForm


def generate_pdf_thumbnail(pdf_path):
    # Open the PDF
    doc = fitz.open(pdf_path)
    # Get the first page
    page = doc.load_page(0)
    # Generate a pixmap from the page
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    # Convert to a PIL image
    img = Image.open(io.BytesIO(pix.tobytes()))
    return img

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFFileForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.save()

            # Generate thumbnail
            thumbnail_image = generate_pdf_thumbnail(pdf_file.file.path)

            # Save the thumbnail to the model
            thumbnail_io = io.BytesIO()
            thumbnail_image.save(thumbnail_io, format='PNG')
            pdf_file.thumbnail.save(f'{pdf_file.file.name}.png', File(thumbnail_io))

            # Extract and save the text from the PDF
            text = extract_text_from_pdf(pdf_file.file.path)
            pdf_file.text = text

            # Generate and save the audio file
            audio_file_path = text_to_speech(text, pdf_file.file.name)
            pdf_file.audio_file = audio_file_path
            pdf_file.save()

            return redirect('pdf_list')
    else:
        form = PDFFileForm()
    return render(request, 'upload.html', {'form': form})


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    return text


def text_to_speech(text, filename):
    tts = gTTS(text=text, lang='en')
    speech_dir = os.path.join(settings.MEDIA_ROOT, 'speech')
    os.makedirs(speech_dir, exist_ok=True)
    base_filename = os.path.splitext(os.path.basename(filename))[
        0]  # Use os.path.basename to get the file name without directory
    speech_path = os.path.join(speech_dir, f'{base_filename}.mp3')

    # Debug print statements
    print(f'Saving speech to {speech_path}')

    # Save the speech file
    tts.save(speech_path)
    return f'speech/{base_filename}.mp3'


def pdf_list(request):
    pdfs = PDFFile.objects.all()
    return render(request, 'pdf_list.html', {'pdfs': pdfs})


def delete_pdf(request, pdf_id):
    pdf = get_object_or_404(PDFFile, id=pdf_id)
    if pdf.audio_file:
        if os.path.exists(pdf.audio_file.path):
            os.remove(pdf.audio_file.path)
    if os.path.exists(pdf.file.path):
        os.remove(pdf.file.path)
    pdf.delete()
    return redirect('pdf_list')


def delete_all_pdfs(request):
    PDFFile.objects.all().delete()
    return redirect('/')


from django.shortcuts import redirect
from .models import PDFFile

def convert_all_pdfs(request):
    pdfs = PDFFile.objects.all()
    for pdf in pdfs:
        if not pdf.audio_file:
            text = extract_text_from_pdf(pdf.file.path)
            audio_file_path = text_to_speech(text, pdf.file.name)
            pdf.audio_file = audio_file_path
            pdf.save()
    return redirect('/pdfs/')


from django.shortcuts import render, redirect

def preferences(request):
    if request.method == 'POST':
        # Save the preferences here, e.g., save to the session or database
        request.session['audio_language'] = request.POST.get('language', 'en')
        return redirect('/preferences/')
    return render(request, 'preferences.html')


from django.shortcuts import render

def help_page(request):
    return render(request, 'help.html')
