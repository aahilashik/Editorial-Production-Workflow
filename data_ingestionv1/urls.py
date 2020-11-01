from django.urls import path
from . import views

urlpatterns = [
    path('gather', views.index, name='index'),
#    path("page1", views.page, name="home"),
]