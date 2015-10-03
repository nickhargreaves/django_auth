from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from forms import CustomRegistrationForm


def index(request):
    return HttpResponseRedirect('/django_auth/login')


# Login function
def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)


# Authentications
def dj_auth(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/django_auth/profile')
    else:
        return HttpResponseRedirect('/django_auth/invalid')


# Show user profile
def profile(request):
    return render_to_response('profile.html', {'full_name': request.user.username})


# No user
def invalid(request):
    return render_to_response('invalid.html')


# Logout
def logout(request):
    auth.logout(request)
    return render_to_response('logout.html')


# Register user
def register_user(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/django_auth/register_success')

    args = {}
    args.update(csrf(request))

    args['form'] = CustomRegistrationForm()

    return render_to_response('register.html', args)


# Register success
def register_success(request):
    return render_to_response('register_success.html')
