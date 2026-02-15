from django.urls import path, re_path

from scans import views

app_name = 'scans'
urlpatterns = [
    path('completion', views.completion),
    path('publication/<str:code>', views.publication, name='publication'),
    path('publication', views.publication, name='publication'),
    path('', views.publications, name='publications'),
    path('pdf', views.pdf_proxy, name='pdf'),
    path('file/<int:scan_id>', views.pdf_proxy, name='file'),
    path('file/<int:scan_id>/<str:file_name>', views.pdf_proxy, name='file'),
    re_path('file/<int:scan_id>/(?P<path>.*)$', views.pdf_proxy, name='file'),

    path('scans', views.scans, name='scans'),
    path('renumber', views.renumber, name='renumber'),
    path('identify', views.identify, name='identify'),
    path('cover', views.cover, name='cover'),
    path('cover/<int:issue>', views.cover, name='cover'),
    path('fileinfo', views.issue_info, name='fileinfo'),
]
