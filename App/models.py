'''from django.db import models

class Uploads(models.Model):
    image=models.ImageField(upload_to='documents/')
    name=models.CharField(max_length=20,null=True)

class UploadFileSingle(models.Model):
    file        = models.FileField(upload_to='files/%Y/%m/%d', models.FilePath)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    models.FilePathField.recursive = True
    models.FilePathField.allow_folders = True
    updated_at  = models.DateTimeField(auto_now=True)

    def some_folder = FilePathField(path='some_path', recursive=True, allow_files=True, allow_folders=True,)'''

from __future__ import unicode_literals

from django.db import models


class Photo(models.Model):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
