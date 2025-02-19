from django.urls import path

from .views import *


app_name = 'images'

urlpatterns = [
    path('create/', image_create, name='create'),
    path('detail/<int:id>/', image_detail, name='detail'),
    ]