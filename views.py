import json
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.utils import timezone
from forms import CustomRegistrationForm

from django_auth.models import UserProfile
import datetime, random, hashlib
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from twilio.rest import TwilioRestClient
from django.conf import settings
import random


def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/django_auth/profile')
    else:
        args = {}
        args.update(csrf(request))

        args['form'] = CustomRegistrationForm()
        args['page_title'] = "Login / Sign Up"

        return render_to_response('login_register.html', args)


# Register user
def register_user(request):
    form = CustomRegistrationForm(request.POST)
    if form.is_valid():
        form.save()

        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        activation_key = hashlib.sha1(salt + email).hexdigest()
        key_expires = timezone.make_aware(datetime.datetime.today() + datetime.timedelta(2),
                                          timezone.get_default_timezone())
        # Retrieve user
        user = User.objects.get(username=username)

        # Save profile
        new_profile = UserProfile(user=user, activation_key=activation_key,
                                  key_expires=key_expires, phone_number=phone, username=username)
        new_profile.save()


        # Send email with activation key
        email_subject = 'Account confirmation'
        email_body = "Hi %s, you have successfully registered but just one last step to get started. To activate your account, click this link within \
        48hours https://hidden-reef-1355.herokuapp.com/django_auth/confirm/%s. You will also receive a message on your phone number %s to confirm your number." % (
            username, activation_key, new_profile.phone_number)

        send_mail(email_subject, email_body, 'mail@localhost', [email], fail_silently=False)

        return HttpResponseRedirect('/django_auth/register_success')
    else:
        return HttpResponseRedirect('/django_auth/')


# Authentications
def dj_auth(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        # get user profile
        user_profile = get_object_or_404(UserProfile,
                                         username=username)
        # send confirmation code
        confirm_code = str(random.randint(1111, 9999))
        send_sms(user_profile.phone_number, "Your confirmation code is " + confirm_code)

        # add code to user profile
        user_profile.sms_activation = confirm_code
        user_profile.save()

        # take to confirm login code screen
        params = {'username': username, 'password': password, 'phone':user_profile.phone_number, 'page_title':"Confirm Login Code"}  # TODO: find more secure way
        params.update(csrf(request))

        return render_to_response('confirm_login.html', params)

    else:
        return HttpResponseRedirect('/django_auth/invalid')


# Process login confirmation code
def confirm_login_code(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        confirm_code = request.POST.get('confirm_code', '')

        user_profile = get_object_or_404(UserProfile,
                                         sms_activation=confirm_code)
        # check if is correct confirmation code
        if user_profile.sms_activation == confirm_code:
            # login user
            auth.login(request, user)
            # reset confirm code
            user_profile.sms_activation = "000"
            user_profile.save()
            # take to profile
            return HttpResponseRedirect('/django_auth/profile')
        else:
            return HttpResponseRedirect('/django_auth/invalid_code')
    else:
        return HttpResponseRedirect('/django_auth/invalid')


# Show user profile
def profile(request):
    return render_to_response('profile.html',
                              {'full_name': request.user.username, 'page_title':'Profile'})


# No user
def invalid(request):
    return render_to_response('invalid.html', {'page_title':'Invalid credentials'})


# Logout
def logout(request):
    auth.logout(request)
    return render_to_response('logout.html', {'page_title':'Logout'})


# Register success
def register_success(request):
    return render_to_response('register_success.html', {'page_title':'Registration successfull'})


# Process email confirmation
def confirm(request, activation_key):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/django_auth/')
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires < timezone.make_aware(datetime.datetime.today(), timezone.get_default_timezone()):
        return render_to_response('invalid_code.html', {'page_title':'Invalid code'})

    # generate random confirmation code
    confirm_code = str(random.randint(1111, 9999))
    send_sms(user_profile.phone_number, "Your confirmation code is " + confirm_code)

    # add confirmation code to user profile
    user_profile.sms_activation = confirm_code
    user_profile.save()

    params = {'success': True, 'phone': user_profile.phone_number, 'page_title':'Confirm code'}
    params.update(csrf(request))

    return render_to_response('confirm.html', params)


# Process reg confirmation code
def confirm_reg_code(request):
    confirm_code = request.POST.get('confirm_code', '')

    user_profile = get_object_or_404(UserProfile,
                                     sms_activation=confirm_code)
    # check if is correct confirmation code
    if user_profile.sms_activation == confirm_code:
        # set to active
        user_account = user_profile.user
        user_account.is_active = True
        user_account.save()
        # reset confirm code
        user_profile.sms_activation = "000"
        user_profile.save()

        # take to login
        args = {}
        args.update(csrf(request))

        args['form'] = CustomRegistrationForm()
        args['confirmed'] = "You have successfully confirmed your phone number!"
        args['page_title'] = "Successful confirmation"

        return render_to_response('login_register.html', args)
    else:
        return HttpResponseRedirect('/django_auth/invalid_code')


# Send SMS
def send_sms(send_to, send_message):
    account = settings.TWILLIO_ACCOUNT
    token = settings.TWILLIO_TOKEN
    client = TwilioRestClient(account, token)

    client.messages.create(to=send_to, from_=settings.TWILLIO_FROM,
                           body=send_message)
    return None
