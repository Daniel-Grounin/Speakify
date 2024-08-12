from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_pdf, name='upload_pdf'),
    path('pdfs/', views.pdf_list, name='pdf_list'),
    path('delete/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),
    path('delete-all-pdfs/', views.delete_all_pdfs, name='delete_all_pdfs'),
    path('convert-all-pdfs/', views.convert_all_pdfs, name='convert_all_pdfs'),
    path('preferences/', views.preferences, name='preferences'),
    path('help/', views.help_page, name='help_page'),
]
