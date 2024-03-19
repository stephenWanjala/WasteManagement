from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geos import Point
from django.shortcuts import render, redirect

from accounts.models import CustomUser
from wasteman.models import WasteCollector, Resident


# Create your views here.
def loginPage(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect(to='/admin')
        redirect(to='home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect(to='/admin')
            return redirect(to='home')
        else:
            messages.info(request, 'Email or password is incorrect')
    context = {'messages': messages.get_messages(request=request), 'currentYear': datetime.now().year}
    return render(request=request, template_name='accounts/login.html', context=context)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        is_collector = request.POST.get('is_collector')

        if password1 == password2:
            # Create the user
            user = CustomUser.objects.create_user(email=email, password=password1, phone_number=phone_number,
                                                  first_name=first_name, last_name=last_name)
            # user.save()

            # Get user's location using GeoIP2
            try:
                geoip_reader = GeoIP2()
                ip_address = request.META.get('REMOTE_ADDR')
                response = geoip_reader.city(ip_address)
                user_location = Point(response.longitude, response.latitude)
                user.location = user_location
                print("User location: ")
                print(user.location)
                user.save()
            except Exception as e:
                messages.error(request, f'Failed to get user location: {e}')

            # Create either a resident or a collector
            if is_collector == 'on':
                WasteCollector.objects.create(user=user)
                user.is_resident = False
                user.is_collector = True
                user.save()
            else:
                Resident.objects.create(user=user)
                user.is_resident = True
                user.is_collector = False
            user.save()

            # Authenticate and login the user
            user = authenticate(request, username=email, password=password1)
            if user is not None:
                login(request=request, user=user)
                messages.success(request, 'Registration successful. You are now logged in.')
                return redirect('home')
            else:
                messages.error(request, 'Failed to log in after registration.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'accounts/register.html')


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect(to='login')
