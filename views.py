import json
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from forms import CustomRegistrationForm

from django_auth.models import UserProfile
import datetime, random, hashlib
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from twilio.rest import TwilioRestClient
from django.conf import settings

def index(request):
    args = {}
    args.update(csrf(request))

    args['form'] = CustomRegistrationForm()

    return render_to_response('login_register.html', args)


# Register user
def register_user(request):
    form = CustomRegistrationForm(request.POST)
    if form.is_valid():
        form.save()

        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        activation_key = hashlib.sha1(salt + email).hexdigest()
        key_expires = datetime.datetime.today() + datetime.timedelta(2)

        # Retrieve user
        user = User.objects.get(username=username)

        # Save profile
        new_profile = UserProfile(user=user, activation_key=activation_key,
                                  key_expires=key_expires)
        new_profile.save()

        # Send email with activation key
        email_subject = 'Account confirmation'
        email_body = "Hi %s, you have successfully registered but just one last step to get started. To activate your account, click this link within \
        48hours https://hidden-reef-1355.herokuapp.com/django_auth/confirm/%s" % (username, activation_key)

        # send_mail(email_subject, email_body, 'mail@localhost', [email], fail_silently=False)

        return HttpResponseRedirect('/django_auth/register_success')
    else:
        return HttpResponseRedirect('/django_auth/')


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


# Register success
def register_success(request):
    return render_to_response('register_success.html')


# Confirm email
def confirm(request, activation_key):
    if request.user.is_authenticated():
        return render_to_response('confirm.html', {'has_account': True})
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires < datetime.datetime.today():
        return render_to_response('confirm.html', {'expired': True})
    user_account = user_profile.user
    user_account.is_active = True
    user_account.save()
    return render_to_response('confirm.html', {'success': True})


# Send SMS
def send_sms(request):
    
    send_to = request.POST.get('number', '')
    send_message = request.POST.get('message', '')

    account = settings.TWILLIO_ACCOUNT
    token = settings.TWILLIO_TOKEN
    client = TwilioRestClient(account, token)

    client.messages.create(to=send_to, from_=settings.TWILLIO_FROM,
                                     body=send_message)
    return render_to_response('enter_code.html')
