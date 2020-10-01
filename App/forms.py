from django import forms

class UploadForm(forms.Form):
    CHOICES = (('0','PDF'), ('1','ODT'),('2',"Image"),('3',"PPTX"))
    #mode = forms.ChoiceField(widget=forms.Select, choices=CHOICES,label="")
    image=forms.FileField(label='',)

class CommentForm(forms.Form):
    comment=forms.Textarea()

