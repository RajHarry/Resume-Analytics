'''from django.conf.urls import url
from . import views
appName = "myApp"
urlpatterns = [
    url(r'^DeepAgri/$',views.DeepAgri.as_view(),name='DeepAgri'),
    url(r'^home/$', views.home,name="index"),
    url(r'^upload_comment/$',views.Comment.as_view(),name='comments')
]'''
from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    # url(r'^$', views.get_index, name='index'),
    # url(r'^Upload$', views.post_upload_images, name='Upload'),
    # url(r'^Upload/.*$', views.get_score, name='Resume Score'),
    path('', views.get_index, name='index'),
    path('Upload', views.post_upload_images, name='Upload'),
    url(r'^Upload/.*$', views.get_score, name='Resume Score'),

]
