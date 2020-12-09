from . import views
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path('gather', views.index, name='index'),
    path('contact', views.contact, name='contact'),
    path('myfiles', views.submissions, name='submissions'),
    path('download/<str:id>/<str:file>', views.filesDownload, name='download file'),
    path('delete/<str:id>/<str:file>', views.filesDelete, name='delete file'),
    
#    path('page1', views.page, name="home"),
]