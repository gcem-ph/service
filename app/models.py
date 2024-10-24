from django.db import models
from django.utils.dateparse import parse_duration
import os
from datetime import datetime
from configs.choises import EQUIPMENT_TYPES, ENGINEERS, DOWNTIME_STATUS
from django_ckeditor_5.fields import CKEditor5Field
from colorfield.fields import ColorField

# Create your models here.

class Engineer(models.Model):
    engineer_id = models.AutoField(primary_key=True)
    full_name = models.CharField(verbose_name='Full Name', null=True, max_length=100)
    company = models.CharField(verbose_name='Company', null=True, max_length=100)

    def __str__(self):
        return f'{self.full_name} - {self.company}'

class Equipment(models.Model):
    equipment_id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='Name', null=True, blank=True, max_length=100)
    equipment_type = models.CharField(verbose_name='Type', choices=EQUIPMENT_TYPES, null=True, blank=True, max_length=100)
    manufacturer = models.CharField(verbose_name='Manufacturer', null=True, blank=True, max_length=100)
    serial_number = models.CharField(verbose_name='S/N', null=True, blank=True, max_length=100)
    installed_on = models.DateField(verbose_name='Installation Date', null=True, blank=True, max_length=100)
    installed_by = models.CharField(verbose_name='Installed By', null=True, blank=True, max_length=100)
    
    decommissioned_on = models.DateField(verbose_name='Decommission Date', null=True, blank=True, max_length=100)
    extra_notes = CKEditor5Field('Notes', config_name='extends', null=True, blank=True)

    def path(self, filename):  
        date = str(datetime.now().strftime("%d.%m.%Y"))
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return os.path.join('Manuals', f'{self.equipment_type}, {self.name}', str(date + '-' + filename))

    manuals = models.FileField(upload_to=path, blank=True, max_length=2000)

    def __str__(self):
        return f'{self.name}'

class Status(models.Model):

    COLOR_PALETTE = [
        ("#FF6347", "red", ),
        ("#9ACC32", "yellowgreen", ),
        ("#008080", "green", ),
        ("#FF64A2", "purple", ),
    ]

    name = models.CharField('Severity', null=True, max_length=100, blank=True)
    severity = models.IntegerField('Severity code', null=True, blank=True)
    color = ColorField(samples=COLOR_PALETTE, null=True, blank=True)
    description = models.CharField('Description', max_length=1000, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'
    
class Part(models.Model):
    name = models.CharField(verbose_name='Microscope Part', max_length=200, null=True)

    def __str__(self):
        return f'{self.name}'


class ServiceCall(models.Model):
    service_call_id = models.AutoField(primary_key=True)
    title = models.CharField('Problem Title', max_length = 100, null=True)
    created = models.DateField(null=True)
    opened = models.DateField(null=True, blank=True)
    closed = models.DateField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    call_id = models.CharField('Call ID', max_length = 20, blank=True)
    key_words = models.CharField('Key words', max_length = 20, blank=True)
    description = models.CharField('Problem Description', max_length = 100)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, related_name='equipment_service_call', null=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, related_name='status_service_call', null=True)
    system_part = models.ForeignKey(Part, on_delete=models.SET_NULL, related_name='part_service_call', null=True)
    user_notes = CKEditor5Field('User\'s Notes', config_name='extends', null=True, blank=True)
    service_notes = models.CharField('Service\'s Notes', null=True, blank=True, max_length=1000)
    
    def __str__(self):
        return f'{self.service_call_id} - {self.equipment} - {self.title}'

class Downtime(models.Model):
    service_call = models.ForeignKey(ServiceCall, on_delete=models.SET_NULL, related_name='downtime_service_call', null=True) 
    downtime_id = models.AutoField(primary_key=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    start = models.DateTimeField(verbose_name='Downtime Start', null=True)
    end = models.DateTimeField(verbose_name='Downtime End', null=True, blank=True)
    duration = models.DurationField(verbose_name='Downtime (days, seconds)', null=True, blank=True) 
    hours = models.FloatField(verbose_name='Hours', null=True, blank=True)
    status = models.CharField(verbose_name='Downtime Status', choices=DOWNTIME_STATUS, null=True,  max_length=100)
    engineer = models.ForeignKey(Engineer, on_delete=models.SET_NULL, related_name="downtime_engineer", null=True)
    #engineer = models.CharField(verbose_name='Assigned Engineer', choices=ENGINEERS, null=True, blank=True, max_length=100)
    notes = models.CharField('Notes', max_length=1000, blank=True)
    
    def save(self, *args, **kwargs):
        
        if self.end:
            self.duration = self.end - self.start
            self.hours = self.duration.total_seconds() / 3600
            super(Downtime, self).save(*args, **kwargs)
        else:
            super(Downtime, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.service_call} - {self.start}:{self.end} - {self.status} - {self.engineer}'


class ServiceReport(models.Model):
    
    def path(self, filename):  
        date = str(datetime.now().strftime("%d.%m.%Y"))
        return os.path.join('Field_Service_Reports', self.service_call.equipment.name, str(date + '-' + filename))
    
    service_call = models.ForeignKey(ServiceCall, on_delete=models.SET_NULL, related_name='report_service_call', null=True) 
    service_report_id = models.AutoField(primary_key=True)
    uploaded = models.DateTimeField(auto_now=True, null=True)
    service_report = models.FileField(upload_to=path, max_length=1000)

    def filename(self):
        return os.path.basename(self.service_report.path)

    def __str__(self):
        return f'{self.service_call}'
    

    
