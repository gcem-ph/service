from django.contrib import admin
from configs import settings
from app.models import Equipment, ServiceCall, Downtime, ServiceReport, Status, Part, Engineer
# Register your models here.

admin.site.register(Equipment)
admin.site.register(ServiceCall)
admin.site.register(Downtime)
admin.site.register(ServiceReport)
admin.site.register(Status)
admin.site.register(Part)
admin.site.register(Engineer)
admin.site.site_url = '/' + settings.SCRIPT_NAME