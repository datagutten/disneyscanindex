from django.urls import path

from . import views

app_name = 'opds'
urlpatterns = [
    path('', views.publications, name='publications'),
    path('publication/<str:code>', views.publication, name='publication'),
    path('publication/<str:code>/<int:year>', views.publication, name='publication'),
    path('issue/<str:code>', views.issue, name='issue'),
]
