from django.forms import ModelForm, DateInput, DateField
from app.models import ServiceCall, ServiceReport, Downtime
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget


class DateInput(DateInput):
    input_type = 'date'

class ServiceCallForm(ModelForm):

    created= DateField(
        required = True,
        input_formats=['%d-%m-%Y'], 
        widget=DateInput(
            format = '%d-%m-%Y',
    ))

    opened= DateField(
        required = False,
        input_formats=['%d-%m-%Y'], 
        widget=DateInput(
            format = '%d-%m-%Y',
    ))

    closed= DateField(
        required = False,
        input_formats=['%d-%m-%Y'], 
        widget=DateInput(
            format = '%d-%m-%Y',
    ))

    user_notes = forms.CharField(
        required=False,
        widget=CKEditor5Widget(),
        )

    class Meta:
        model = ServiceCall
        fields = '__all__'

class ServiceReportForm(ModelForm):

    class Meta:
        model = ServiceReport
        fields = '__all__'

class DowntimeForm(ModelForm):

    start= DateField(
        required = True,
        input_formats=['%d-%m-%Y %H:%M:%S'], 
        widget=DateInput(
            format = '%d-%m-%Y %H:%M',
    ))

    end= DateField(
        required = False,
        input_formats=['%d-%m-%Y %H:%M:%S'], 
        widget=DateInput(
            format = '%d-%m-%Y %H:M',
    ))

    class Meta:
        model = Downtime
        fields = '__all__'