from django.urls import path
from . import views


urlpatterns = [
    path('', views.main, name='main'),
    path('diskviewer/', views.yandex_disk_request, name='diskviewer'),
]
