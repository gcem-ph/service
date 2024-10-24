from django.shortcuts import render, redirect
from django.http import HttpResponse 
from django.core.files.storage import FileSystemStorage
import datetime
from django.db.models import Avg, Max, Min, Sum, Count, Q, F
from app.models import ServiceCall, Equipment, Downtime, ServiceReport
from app.forms import ServiceCallForm, ServiceReportForm, DowntimeForm
from django.utils.timezone import make_aware
import app.utils as utils
import random
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def home(request):
    context = {}
    context['total_calls'] = ServiceCall.objects.all().count
    context['calls_opened'] = ServiceCall.objects.filter(opened__lt=datetime.datetime.today()).count()
    context['calls_closed'] = ServiceCall.objects.filter(closed__lt=datetime.datetime.today()).count()
    context['call_avg_closing_time'] = ServiceCall.objects.aggregate(avg=Avg(F('closed') - F('created')))
    context['call_max_closing_time'] = ServiceCall.objects.aggregate(max=Max(F('closed') - F('created')))
    context['call_min_closing_time'] = ServiceCall.objects.aggregate(min=Min(F('closed') - F('created')))
    
    context['system_installed'] = Equipment.objects.filter(equipment_type='microscope').count
    context['systems_running'] = ServiceCall.objects.filter(status__name="Up & Running").count
    
    
    
    context['downtime_entries'] = Downtime.objects.count

    context['down_systems'] = ServiceCall.objects.filter(status__name="Down").count
    context['down_entries'] = Downtime.objects.filter(status="down").count
    context['down_time'] = Downtime.objects.filter(status="down").aggregate(time=Sum('hours'))
    context['down_avg'] = Downtime.objects.filter(status="down").aggregate(time=Avg('hours'))
    context['down_max'] = Downtime.objects.filter(status="down").aggregate(time=Max('hours'))
    context['down_min'] = Downtime.objects.filter(status="down").aggregate(time=Min('hours'))
    
    context['up_with_issues_systems'] = ServiceCall.objects.filter(status__name="Up with Issues").count
    context['up_with_issues_entries'] = Downtime.objects.count
    context['up_with_issues_time'] = Downtime.objects.filter(status="up-with-issues").aggregate(time=Sum('hours'))
    context['up_with_issues_avg'] = Downtime.objects.filter(status="up-with-issues").aggregate(time=Avg('hours'))
    context['up_with_issues_max'] = Downtime.objects.filter(status="up-with-issues").aggregate(time=Max('hours'))
    context['up_with_issues_min'] = Downtime.objects.filter(status="up-with-issues").aggregate(time=Min('hours'))


    context['downtime_by_part'] = ServiceCall.objects.count
    context['downtime_by_microscope'] = utils.chart_js_stacked_bar(ServiceCall.objects.all()
                                                             .values(microscope=F('equipment__name'), downtime=F('downtime_service_call__status'))
                                                             .annotate(time=Sum('downtime_service_call__hours')))
    
    context['downtime_by_microscope_by_part'] = utils.convert_to_stacked_grouped_data(ServiceCall.objects.all()
                                                                                      .values(microscope=F('equipment__name'), 
                                                                                              downtime=F('downtime_service_call__status'),
                                                                                              part=F('system_part__name'))
                                                                                              .exclude(downtime__isnull=True)
                                                                                              .annotate(time=Sum('downtime_service_call__hours')))
    context['engineer_visits'] = ServiceCall.objects.count

    return render(request, "home.html", context)


def status(request):
    context = []
    equipment = Equipment.objects.all()

    for tool in equipment:
        tools = {}
        tool_status = ServiceCall.objects.filter(equipment__name=tool.name, status__severity__lte=10).order_by('updated')
        tools["equipment"] = tool.name
        tools["status"] = tool_status.order_by('status__severity').values(severity=F('status__name')).first()
        tools["code"] = tool_status.order_by('status__severity').values(code=F('status__severity')).first()
        tools["color"] = tool_status.order_by('status__severity').values(color=F('status__color')).first()
        tools["calls"] = tool_status.order_by('status__severity')
        tools["updated"] = tool_status.order_by('status__severity').values(last=F('updated')).first()
        tools["id"] = tool_status.order_by('status__severity').values(id=F('service_call_id')).first()
        context.append(tools)
    
    return render(request, "status.html", {'context' : context})

@login_required(redirect_field_name="login")
def calls(request):
    context = {}
    context['calls'] = ServiceCall.objects.all().order_by('-updated')
    return render(request, "calls.html", context)

@login_required(redirect_field_name="login")
def call_details(request, service_call_id):
    call_instance = ServiceCall.objects.get(service_call_id=service_call_id)
    downtime_instance = Downtime.objects.filter(service_call__service_call_id=service_call_id)
    report_instance = ServiceReport.objects.filter(service_call__service_call_id=service_call_id)

    call_form = ServiceCallForm(instance=call_instance)
    # call_form.fields['user_notes'].widget.attrs['id'] = 'id_user_notes_' + str(service_call_id)
    downtime_form = DowntimeForm()
    downtime_form.initial={"service_call" : service_call_id}
    report_form = ServiceReportForm(initial={"service_call" : service_call_id})

    engineers_assigned = Downtime.objects.filter(service_call__service_call_id=service_call_id).values('engineer').annotate(Count('engineer', distinct=True))
    
    context = {}
    context['call'] = call_instance
    context['downtimes'] = downtime_instance
    context['reports'] = report_instance
    context['call_form'] = call_form
    context['downtime_form'] = downtime_form
    context['report_form'] = report_form
    if call_instance.closed:
        context['days_to_solve_issue'] = ( call_instance.closed - call_instance.created).days
    context['days_since_issues_opened'] = ( datetime.datetime.now(datetime.timezone.utc).date() - call_instance.created ).days
    context['engineers_assigned'] = len(engineers_assigned)
    context['downtime_entries'] = downtime_instance.count
    context['reports_entries'] = report_instance.count
    context['total_hours_of_downtime'] = downtime_instance.aggregate(time=Sum('hours'))
    context['last_worked_call'] = downtime_instance.order_by('updated').last()
    context['downtime_hours'] = downtime_instance.filter(status='down').values('status').aggregate(time=Sum('duration'))
    context['up_with_issues_hours'] = downtime_instance.filter(status='up-with-issues').values('status').aggregate(time=Sum('duration'))
    context['engineer_time'] = list(downtime_instance.values('engineer').order_by('engineer').annotate(time=Sum('hours')))

    if request.method == 'POST':
        form = ServiceCallForm(request.POST or None, instance=call_instance)

        if request.POST.get('closed'):
            if request.POST.get('closed') < request.POST.get('created'):
                messages.error(request, "Closed date must be later than created!")
                return redirect('call_details', service_call_id=call_instance.service_call_id)

        if form.is_valid():
            form.save()
            messages.success(request, 'Changes successfully saved!')
            return redirect('call_details', service_call_id=call_instance.service_call_id)
        else:
            print(form.errors)
            form = ServiceCallForm(request.POST or None, instance=call_instance)
            return redirect('call_details', service_call_id=call_instance.service_call_id)

    return render(request, "call_details.html", context=context)

@login_required(redirect_field_name="login")
def new_call(request):
    new_call_form = ServiceCallForm()

    if request.method == 'POST':
        new_call_form = ServiceCallForm(request.POST or None)
        new_call_form.fields['user_notes'].widget.attrs['id'] = 'new_call_form' + str(random.randint(1,100))
        if new_call_form.is_valid():
            new_call_form.save()
            return redirect('calls')
        else:
            print(new_call_form.errors)
            new_call_form = ServiceCallForm()
    return render(request, 'includes/new_call.html', {'call_form' : new_call_form,})

@login_required(redirect_field_name="login")
def call(request, service_call_id):
    call_instance = ServiceCall.objects.get(service_call_id=service_call_id)
    form = ServiceCallForm(instance=call_instance)
    form.fields['user_notes'].widget.attrs['id'] = 'id_user_notes_' + str(service_call_id)

    # if request.method == 'POST':
    #     created = request.POST.get('created')
    #     opened = request.POST.get('opened')
    #     closed = request.POST.get('closed')
        
    #     if created > opened or created > closed:
    #         return redirect('call_details', service_call_id=call_instance.service_call_id)

    form = ServiceCallForm(request.POST or None, instance=call_instance)
    if form.is_valid():
        form.save()
        return redirect('call_details', service_call_id=call_instance.service_call_id)
    else:
        print(form.errors)
        form = ServiceCallForm(request.POST or None, instance=call_instance)
        return redirect('call_details', service_call_id=call_instance.service_call_id)
    
    # return render(request, 'includes/call.html', {'call' : call_instance,})
    
@login_required(redirect_field_name="login")
def reports(request, service_call_id):
    call_instance = ServiceCall.objects.get(service_call_id=service_call_id)
    report_instance = ServiceReport.objects.filter(service_call__service_call_id=service_call_id)
    form = ServiceReportForm(request.POST or None, initial={"service_call" : service_call_id})
    
    if request.method == 'POST' and request.FILES:
        upload_report = request.FILES.get('service_report')
        report_obj = ServiceReport(
            service_call = call_instance,
            service_report = upload_report
        )
        report_obj.save()
        return redirect('call_details', service_call_id=call_instance.service_call_id)
    else:
        print(form.errors)
        return redirect('call_details', service_call_id=call_instance.service_call_id)

   
@login_required(redirect_field_name="login")
def downtimes(request, service_call_id):
    call_instance = ServiceCall.objects.get(service_call_id=service_call_id)
    downtime_instance = Downtime.objects.filter(service_call__service_call_id=service_call_id)
    form = DowntimeForm()
    form.initial={"service_call" : service_call_id}

    if request.method == 'POST':
        form = DowntimeForm(request.POST or None)
        form.data._mutable = True
        form.data['service_call'] = service_call_id
        form.data._mutable = False
        if form.is_valid():
            form.save()
            return redirect('call_details', service_call_id=call_instance.service_call_id)
        else:
            print(form.errors)
            return redirect('call_details', service_call_id=call_instance.service_call_id)
    # return redirect('call_details', service_call_id=call_instance.service_call_id)
    
@login_required(redirect_field_name="login")
def downtime(request, downtime_id):
    downtime_instance = Downtime.objects.get(downtime_id=downtime_id)
    form = DowntimeForm(instance=downtime_instance)

    if request.method == 'POST':
        form = DowntimeForm(request.POST or None, instance=downtime_instance)
        form.data._mutable = True
        form.data['service_call'] = downtime_instance.service_call.service_call_id
        form.data._mutable = False
        if form.is_valid():
            form.save()
            return redirect('call_details', service_call_id=downtime_instance.service_call.service_call_id)
        else:
            print(form.errors)
            return render(request, 'downtime.html', {'downtime_form' : form, 'downtime' : downtime_instance})
    return render(request, 'downtime.html', {'downtime_form' : form, 'downtime' : downtime_instance})
    
