from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from accounts.forms import IssueReportForm
from wasteman.models import Waste, Schedule, IssueReport, PickupZone, Resident, WasteCollector, CollectionStatus


@login_required(login_url='login')
def home(request):
    user = request.user

    if user.is_superuser:
        return redirect('admin')

    try:  # Check if the user is a resident
        resident = get_object_or_404(Resident, user=user)
        if resident:
            waste_summary = Waste.objects.filter(user=user)
            recent_issues = IssueReport.objects.filter(user=user)[:5]
            upcoming_schedules = Schedule.objects.all()[:5]
            pickup_zones = PickupZone.objects.all()

            if request.method == 'POST':
                # Handle waste entry form submission
                form = IssueReportForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Issue reported successfully')
                    return redirect('home')
                else:
                    messages.error(request, 'Error submitting issue report')

            # Render home page for resident
            context = {
                'waste_summary': waste_summary,
                'recent_issues': recent_issues,
                'upcoming_schedules': upcoming_schedules,
                'pickup_zones': pickup_zones,
                'is_resident': True,
                'form': IssueReportForm(),
            }
            print(f"User: {user} - Resident: {resident} - Waste Summary: {waste_summary}")
            return render(request, 'wasteman/home.html', context)


    except Exception as e:
        # Check if the user is a waste collector
        collector = get_object_or_404(WasteCollector, user=user)
        if collector:
            # Get schedules without assigned collectors
            unassigned_schedules = Schedule.objects.filter(waste_collectors__isnull=True)

            if request.method == 'POST':
                # Add collector to schedule
                schedule_id = request.POST.get('schedule_id')
                schedule = get_object_or_404(Schedule, pk=schedule_id)

                if not schedule.waste_collectors.exists():
                    # Add collector to the schedule
                    schedule.waste_collectors.add(collector)
                    messages.success(request, 'You have been assigned to the schedule')

            # Get schedules assigned to the collector
            assigned_schedules = Schedule.objects.filter(waste_collectors=collector)

            # Render home page for waste collector
            context = {
                'unassigned_schedules': unassigned_schedules,
                'assigned_schedules': assigned_schedules,
                'is_collector': True,
            }
            return render(request, 'wasteman/home.html', context)


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


@login_required(login_url='login')
def update_status(request, collection_status_id):
    collection_status = get_object_or_404(CollectionStatus, pk=collection_status_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in ['In Progress', 'Completed']:  # Validate the new_status
            collection_status.status = new_status
            collection_status.save()
            messages.success(request, 'Collection status updated successfully')
        else:
            messages.error(request, 'Invalid status update: Status must be "In Progress" or "Completed"')

    return redirect('home')
