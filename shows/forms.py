from django import forms
from .models import Series,Episode,Media
from django.conf import settings

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'audience' or field_name == 'typ':
                field.widget.attrs['class'] = 'custom-control-input'
            elif field_name is 'banner':
                field.widget.attrs['class'] = 'form-inline'
            else:
                field.widget.attrs['class'] = 'form-control'
            if field_name == 'datestr':
                field.input_formats = settings.DATE_INPUT_FORMATS # what if this isn't in settings?

            field.widget.attrs['placeholder'] = field.help_text

class SeriesForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super(SeriesForm, self).__init__(*args, **kwargs)
        self.fields['rssfeedid'].required = False

    class Meta:
        model = Series
        fields = ['title','seotitle','overview','rssfeedid','audience']
        widgets = {
            'audience': forms.RadioSelect(),
            'overview': forms.Textarea()
        }
        labels = {
            'title': 'television',
            'seotitle': 'link',
            'overview': 'newspaper-o',
            'rssfeedid': 'rss-square',
            'audience': 'user-circle'
        }
        help_texts = {
            'title': 'Title',
            'seotitle': 'Part of the url: aristia.net/movies/<seotitle here>',
            'overview': 'Synopsis',
            'rssfeedid': 'RSS Feed ID',
            'audience': 'Audience'
        }
        '''
        def as_cust_layout(self):
            return self._html_output(
                normal_row='<div class="input-group"><span class="input-group-addon">%(label)s</span> %(field)s%(help_text)s</div>',
                error_row='%s',
                row_ender='</div>',
                help_text_html=' <span class="helptext">%s</span>',
                errors_on_separate_row=True)

        fields = '__all__' or []
        exclude = ['title']
        error_messages = {
            'name': {
                'max_length': _("This writer's name is too long."),
            },
        }
        '''
class MediaForm(BaseForm):
    class Meta:
        model = Media
        exclude = ['episode','got']
        widgets = {
            'got': forms.RadioSelect(),
            'typ': forms.RadioSelect(),
            'datestr': forms.DateTimeInput(format='%d/%m/%Y')
        }
        labels = {
            'title': 'television',
            'seotitle': 'link',
            'overview': 'newspaper-o',
            'turl': 'link',
            'datestr': 'calendar',
            'typ': 'tag',
            'cert': 'certificate',
            'banner': 'picture-o'
        }
        help_texts = {
            'title': 'Title',
            'seotitle': 'Part of the url: aristia.net/movies/<seotitle here>',
            'overview': 'Synopsis',
            'turl': 'URL for more information',
            'datestr': 'Expected release date',
            'typ': 'Media type',
            'cert': 'Certificate',
            'banner': 'Poster image'
        }