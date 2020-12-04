from django.urls import path
from . import views

urlpatterns = [
    path('', views.review, name='review'),
    path('report/download/<refID>', views.downloadPlag, name ="downloadPlag"),
    path('logs/<refID>', views.logs, name ="logs"),
    path('logs/download/<refID>', views.downloadRnP, name ="downloadRnP"),
    path('spell/<refID>', views.spellLogs, name ="logs"),
    path('spell/download/<refID>', views.downloadSpl, name ="downloadSpl"),
    path('language/<refID>', views.grammLogs, name ="logs"),
    path('language/download/<refID>', views.downloadLang, name ="downloadSpl"),
]