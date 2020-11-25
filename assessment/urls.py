from django.urls import path
from . import views

urlpatterns = [
    path('', views.review, name='review'),
    path('logs/<refID>', views.logs, name ="logs"),
    path('logs/download/<refID>', views.download, name ="download"),
]