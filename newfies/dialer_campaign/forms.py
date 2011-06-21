from django import forms
from django.forms import *
from django.contrib import *
from django.contrib.admin.widgets import *
from django.utils.translation import ugettext_lazy as _
from dialer_campaign.models import *
from dialer_campaign.function_def import *
from datetime import *

import django.forms.widgets
from django.utils.encoding import StrAndUnicode, force_unicode
class MyRadioInput(django.forms.widgets.RadioInput):
	"""
	An object used by RadioFieldRenderer that represents a single
	<input type='radio'>.
	"""
	def __unicode__(self):
		return mark_safe(u'%s' % (self.tag(),))
class MyRadioRenderer(django.forms.widgets.RadioFieldRenderer):
	def render(self):
		"""Outputs a <td> for this set of radio fields."""
		return mark_safe(u'\n'.join([u'%s'
				% force_unicode(w) for w in self]))
	def __iter__(self):
		for i, choice in enumerate(self.choices):
			yield MyRadioInput(self.name, self.value, self.attrs.copy(), choice, i)


class SearchForm(forms.Form):
    """General Search Form with From & To date para."""
    from_date = CharField(label=_('From'), required=False, max_length=10,
    help_text=_("Date Format") + ": <em>YYYY-MM-DD</em>.")
    to_date = CharField(label=_('To'), required=False, max_length=10,
    help_text=_("Date Format") + ": <em>YYYY-MM-DD</em>.")


class FileImport(forms.Form):
    """General Form : CSV file upload"""
    csv_file = forms.FileField(label=_("Upload CSV File "), required=True,
                            error_messages={'required': 'Please upload File'},
                            help_text=_("Browse CSV file"))

    def clean_file(self):
        """Form Validation :  File extension Check"""
        filename = self.cleaned_data["csv_file"]
        file_exts = (".csv", )
        if not str(filename).split(".")[1].lower() in file_exts:
            raise forms.ValidationError(_(u'Document types accepted: %s' % \
            ' '.join(file_exts)))
        else:
            return filename


class Contact_fileImport(FileImport):
    """Admin Form : Import CSV file with phonebook"""
    phonebook = forms.ChoiceField(label=_("Phonebook"),
                                choices=field_list("phonebook"),
                                required=False,
                                help_text=_("Select Phonebook"))

    def __init__(self, user, *args, **kwargs):
        super(Contact_fileImport, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['phonebook', 'csv_file']
        # To get user's phonebook list
        if user: # and not user.is_superuser
            self.fields['phonebook'].choices = field_list(name="phonebook",
                                                          user=user)


class LoginForm(forms.Form):
    """Client Login Form"""
    user = forms.CharField(max_length=30, label=_('Username:'), required=True)
    password = forms.CharField(max_length=30, label=_('Password:'),
               required=True, widget=forms.PasswordInput())


class PhonebookForm(ModelForm):
    """Phonebook ModelForm"""

    class Meta:
        model = Phonebook
        fields = ['name', 'description']
        exclude = ('user',)
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }


class ContactForm(ModelForm):
    """Contact ModelForm"""

    class Meta:
        model = Contact
        fields = ['phonebook', 'contact', 'last_name', 'first_name', 'email',
                  'country', 'city', 'description', 'status',
                  'additional_vars']
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        # To get user's phonebook list
        if user:
            self.fields['phonebook'].choices = field_list(name="phonebook",
                                                          user=user)


class CampaignForm(ModelForm):
    """Campaign ModelForm"""
    campaign_code = forms.CharField(widget=forms.HiddenInput)
    monday  = forms.ChoiceField(choices=DAY_STATUS,
              widget=forms.RadioSelect(renderer=MyRadioRenderer))
    week_day_star = forms.ChoiceField(choices=DAYS, label=_('Week day to start'))
    week_day_end = forms.ChoiceField(choices=DAYS, label=_('Week day to finish'))
    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name', 'description', 'status',
                  'callerid', 'startingdate', 'expirationdate',
                  'aleg_gateway', 'voipapp', 'frequency', 'callmaxduration',
                  'maxretry', 'intervalretry', 'calltimeout', 'extra_data',
                  'phonebook', 'daily_start_time', 'daily_stop_time',
                  #'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  #'saturday', 'sunday'
                  ]
        exclude = ('user', )
        widgets = {
            'description': Textarea(attrs={'cols': 23, 'rows': 3}),
        }
    def __init__(self,  *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].initial = get_unique_code(length=5)
        self.fields['startingdate'].initial = datetime.now()
        self.fields['expirationdate'].initial = datetime.now()


class CampaignAdminForm(ModelForm):
    """Admin Campaign ModelForm"""
    class Meta:
        model = Campaign
        fields = ['campaign_code', 'name', 'description', 'user', 'status',
                  'callerid', 'startingdate', 'expirationdate',
                  'aleg_gateway', 'voipapp', 'extra_data', 'phonebook',
                  'frequency', 'callmaxduration', 'maxretry', 'intervalretry',
                  'calltimeout', 'daily_start_time', 'daily_stop_time',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                  'saturday', 'sunday']

    def __init__(self,  *args, **kwargs):
        super(CampaignAdminForm, self).__init__(*args, **kwargs)
        self.fields['campaign_code'].widget.attrs['readonly'] = True
        self.fields['campaign_code'].initial = get_unique_code(length=5)
        self.fields['startingdate'].initial = datetime.now()
        self.fields['expirationdate'].initial = datetime.now()


NAME_TYPE = (
    (1, _('Last Name')),
    (2, _('First Name')),
)

CHOICE_TYPE = (
    (1, _('Contains')),
    (2, _('Equals')),
    (3, _('Begins with')),
    (4, _('Ends with')),
)


class ContactSearchForm(forms.Form):
    """Search Form on Contact List"""

    contact_no = forms.CharField(label=_('Contact Number:'), required=False,
                           widget=forms.TextInput(attrs={'size': 15}))
    contact_no_type = forms.ChoiceField(label='', required=False, initial=1,
                      choices=CHOICE_TYPE, widget=forms.RadioSelect)
    name = forms.CharField(label=_('Contact Name:'), required=False,
                           widget=forms.TextInput(attrs={'size': 15}))
    phonebook = forms.ChoiceField(label=_('Phonebook:'), required=False)
    status = forms.TypedChoiceField(label=_('Status:'), required=False,
             choices=(('0', _('Inactive')), ('1', _('Active ')),
                      ('2', _('All'))),
             widget=forms.RadioSelect, initial='2')

    def __init__(self, user, *args, **kwargs):
        super(ContactSearchForm, self).__init__(*args, **kwargs)
         # To get user's phonebook list
        if user:
            list = []
            list.append((0, '---'))
            pb_list = field_list("phonebook", user)
            for i in pb_list:
                list.append((i[0], i[1]))
            self.fields['phonebook'].choices = list
