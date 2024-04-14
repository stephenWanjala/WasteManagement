from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import render, get_object_or_404, redirect

from accounts.forms import IssueReportForm
from wasteman.models import Waste, Schedule, IssueReport, WasteType, PickupZone, Resident


@login_required(login_url='login')
def home(request):
    if request.user.is_superuser:
        return redirect('admin')
    try:
        resident = get_object_or_404(Resident, user=request.user.id)
        if resident:
            waste_summary = Waste.objects.all()[:5]
            recent_issues = IssueReport.objects.all()[:5]
            upcoming_schedules = Schedule.objects.all()[:5]
            pickup_zones = PickupZone.objects.all()
            if request.method == 'POST':
                date = request.POST.get('date')
                start_time = request.POST.get('startTime')
                end_time = request.POST.get('endTime')
                waste_type_name = request.POST.get('wasteTypeName')
                waste_type_desc = request.POST.get('wasteTypeDesc')
                pickup_zone_id = request.POST.get('pickupZone')
                quantity = request.POST.get('quantity')

                pickup_zone = get_object_or_404(PickupZone, pk=pickup_zone_id)

                try:
                    with transaction.atomic():
                        waste_type = WasteType.objects.create(name=waste_type_name, description=waste_type_desc)
                        waste_schedule = Schedule.objects.create(date=date, start_time=start_time, end_time=end_time,
                                                                 pickup_zone=pickup_zone)
                        waste = Waste.objects.create(schedule=waste_schedule, quantity=quantity, user=resident.user,
                                                     type=waste_type)

                        messages.success(request, 'Waste entry created successfully')
                        return redirect('home')

                except IntegrityError as e:
                    # Handle unique constraint violation
                    messages.error(request,
                                   'An error occurred while creating a waste entry: Unique constraint violated')
                    print(f"IntegrityError: {e}")

                except Exception as e:
                    # Handle other exceptions
                    messages.error(request, 'An error occurred while creating a waste entry')
                    messages.error(request, f"Error: {e}")
                    print(f"Error: {e}")

                    context = {
                        'waste_summary': waste_summary,
                        'recent_issues': recent_issues,
                        'upcoming_schedules': upcoming_schedules,
                        'pickup_zones': pickup_zones,
                        'messages': messages.get_messages(request=request),
                        'resident': True,
                    }

                return render(request=request, template_name='wasteman/home.html', context=context)

    except Exception as e:
        context = {
            'resident': False,
        }
        return render(request=request, template_name='wasteman/home.html', context=context)


@login_required(login_url='login')
def issue_reports(request):
    user = request.user
    issues = IssueReport.objects.filter(user=user)
    form = IssueReportForm()

    if request.method == 'POST':
        form = IssueReportForm(request.POST)
        if form.is_valid():
            issue_report = form.save(commit=False)
            issue_report.user = user
            issue_report.save()
            messages.success(request, 'Issue reported successfully')
            return redirect('issue_reports')
        else:
            # messages.error(request, 'An error occurred while reporting the issue')
            messages.error(request, f"Error: {form.errors}")

    return render(request=request, template_name='wasteman/issue_reports.html',
                  context={'issues': issues,
                           'form': form,
                           })
