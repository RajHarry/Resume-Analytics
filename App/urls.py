from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_index, name='index'),
    path('Upload', views.post_upload_images, name='Upload'),
    url(r'^Upload/.*$', views.get_score, name='Resume Score'),
]
