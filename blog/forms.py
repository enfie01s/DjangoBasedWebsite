from django import forms
from .models import Post
from django.conf import settings

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm,self).__init__(*args,**kwargs)
        for field_name, field in self.fields.items():
            if field_name is 'image':
                field.widget.attrs['class'] = 'form-inline'
            else:
                field.widget.attrs['class'] = 'form-control'
            if field_name == 'pub_date':
                field.input_formats = settings.DATE_INPUT_FORMATS # what if this isn't in settings?
            field.widget.attrs['placeholder'] = field.help_text

class PostForm(BaseForm):
    #def __init__(self, *args, **kwargs):
    #    super(PostForm, self).__init__(*args, **kwargs)
        #self.fields['intro'].required = False
        #self.fields['date'].required = False

    class Meta:
        model = Post
        fields = '__all__'
        #exclude = ['intro','date']
        widgets = {        
            'pub_date': forms.DateTimeInput(format='%d/%m/%Y')
        }
        labels = {
            'title':'info',
            'seotitle':'link',
            'pub_date':'calendar',
            'image':'picture-o',
            'body':'newspaper-o'
        }
        help_texts = {
            'title':'Title',
            'seotitle':'Part of the url: path/<seotitle here>',
            'pub_date':'Date of the event',
            'image':'Photo of the event',
            'body':'Main text'
        }