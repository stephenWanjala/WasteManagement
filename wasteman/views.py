from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from wasteman.models import Waste, Schedule, IssueReport


# Create your views here.

@login_required(login_url='login')
def home(request):
    waste_summary = Waste.objects.all()[:5]  # Get the latest 5 waste entries
    recent_issues = IssueReport.objects.all()[:5]  # Get the latest 5 issue reports
    upcoming_schedules = Schedule.objects.all()[:5]  # Get the first 5 upcoming pickup schedules

    context = {
        'waste_summary': waste_summary,
        'recent_issues': recent_issues,
        'upcoming_schedules': upcoming_schedules,
    }
    return render(request=request, template_name='wasteman/home.html',context=context)
