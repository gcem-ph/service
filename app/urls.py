
from django.conf.urls.static import static
from django.urls import re_path, path
from app import views
from configs import settings

urlpatterns = [
   re_path(r'^$', views.home, name='home'),
   re_path(r'^home/$', views.home, name='home'),
   re_path(r'^calls/$', views.calls, name='calls'),
   re_path(r'^status/$', views.status, name='status'),
   re_path(r'^new-call/$', views.new_call, name='new_call'),
   re_path(r'^call-details/(?P<service_call_id>[0-9]+)/$', views.call_details, name='call_details'),
   re_path(r'^call/(?P<service_call_id>[0-9]+)/$', views.call, name='call'),
   re_path(r'^reports/(?P<service_call_id>[0-9]+)/$', views.reports, name='reports'),
   re_path(r'^downtimes/(?P<service_call_id>[0-9]+)/$', views.downtimes, name='downtimes'),
   re_path(r'^downtime-details/(?P<downtime_id>[0-9]+)/$', views.downtime, name='downtime'),
]

urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)