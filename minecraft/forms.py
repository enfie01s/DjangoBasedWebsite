from django import forms
from .models import SitePerm,Rank

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class SitePermForm(BaseForm):
    minrank = forms.ModelChoiceField(queryset=Rank.objects.all(), required=False)
    class Meta:
        model = SitePerm
        fields = ['minrank','pl']
        labels = {
            'pl': 'cube',
            'minrank': 'id-badge'
        }
        help_texts = {
            'pl': 'Plugin',
            'minrank': 'Rank'
        }
    def __init__(self, *args, **kwargs):
        super(SitePermForm, self).__init__(*args, **kwargs)
        self.fields['pl'].required = False
        '''
        fields = '__all__'
        exclude = ['title']
        widgets = {
            'pl': forms.Select(empty_label='All'),
            'minrank': forms.Select(attrs={'class':'form-control'}),
        }
        labels = {
            'name': _('Writer'),
        }
        help_texts = {
            'name': _('Some useful help text.'),
        }
        error_messages = {
            'name': {
                'max_length': _("This writer's name is too long."),
            },
        }
        '''
