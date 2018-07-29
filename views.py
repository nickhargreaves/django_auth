import datetime
import hashlib
import random

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context_processors import csrf
from django.urls import reverse
from django.utils import timezone
from twilio.rest import TwilioRestClient

from django_auth.models import UserProfile
from .forms import CustomRegistrationForm


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    else:
        args = {}
        args.update(csrf(request))

        args['form'] = CustomRegistrationForm()
        args['page_title'] = "Login / Sign Up"
        if request.GET.get('invalid', None):
            args['invalid_user'] = True
        if request.GET.get('reg_success', None):
            args['reg_message'] = request.GET.get('reg_message')
        return render_to_response('login_register.html', args)


# Register user
def register_user(request):
    form = CustomRegistrationForm(request.POST)
    if form.is_valid():
        form.save()
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        activation_key = hashlib.sha1((salt + email).encode('utf-8')).hexdigest()
        key_expires = timezone.make_aware(datetime.datetime.today() + datetime.timedelta(2),
                                          timezone.get_default_timezone())
        # Retrieve user
        user = User.objects.get(username=username)

        # Save profile
        new_profile = UserProfile(user=user, activation_key=activation_key,
                                  key_expires=key_expires, phone_number=phone)
        new_profile.save()

        if settings.REQUIRE_EMAIL_VERIFICATION_ON_REGISTER:
            # Send email with activation key
            email_subject = 'Account confirmation'
            email_body = "Hi " + username + ", you have successfully registered but just one last step to get started. " \
                                            "To activate your account, click this link within 48hours " +\
                         "https://www." + Site.objects.get_current().domain + reverse('django_auth.confirm', args=[activation_key]) \
                         + ". You will also receive a message on your phone number " + new_profile.phone_number \
                         + " to confirm your number."
            send_mail(email_subject, email_body, settings.FROM_EMAIL_ADDRESS, [email], fail_silently=False)
            return HttpResponseRedirect(reverse('django_auth') + '?reg_success=True&reg_message='
                                        + 'Account confirmation email sent. Please check your email')
        else:
            return confirm(request, activation_key)
    else:
        args = {}
        args.update(csrf(request))
        args.update({'form': form, 'register': True})
        return render_to_response('login_register.html', args)


# Authentications
def dj_auth(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user:
        # get user profile
        user_profile = get_object_or_404(UserProfile,
                                         user__username=username)
        if settings.REQUIRE_PHONE_VERIFICATION_ON_LOGIN:
            # send confirmation code
            confirm_code = str(random.randint(1111, 9999))
            send_sms(user_profile.phone_number, "Your confirmation code is " + confirm_code)

            # add code to user profile
            user_profile.sms_activation = confirm_code
            user_profile.save()

            # take to confirm login code screen
            params = {'username': username, 'password': password, 'phone': user_profile.phone_number,
                      'page_title': "Confirm Login Code"}  # TODO: find more secure way
            params.update(csrf(request))
            return render_to_response('confirm_login.html', params)
        else:
            request.user_profile = user_profile
            request.bypass_confirm_phone = True
            return confirm_login_code(request)

    else:
        return HttpResponseRedirect(reverse('django_auth') + "?invalid=True")


# Process login confirmation code
def confirm_login_code(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        confirm_code = request.POST.get('confirm_code', '')

        user_profile = request.user_profile if request.user_profile else get_object_or_404(UserProfile,
                                                                                           sms_activation=confirm_code)
        # check if is correct confirmation code
        if user_profile.sms_activation == confirm_code or request.bypass_confirm_phone:
            # login user
            auth.login(request, user)
            # reset confirm code
            user_profile.sms_activation = "000"
            user_profile.save()
            # take to profile
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponseRedirect(reverse('django_auth.invalid_code'))
    else:
        return HttpResponseRedirect(reverse('django_auth.invalid_code'))


# Logout
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


# Process email confirmation
def confirm(request, activation_key):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('django_auth'))
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires < timezone.make_aware(datetime.datetime.today(), timezone.get_default_timezone()):
        return render_to_response('invalid_code.html', {'page_title': 'Invalid code'})

    if settings.REQUIRE_PHONE_VERIFICATION_ON_REGISTER:
        # generate random confirmation code
        confirm_code = str(random.randint(1111, 9999))
        send_sms(user_profile.phone_number, "Your confirmation code is " + confirm_code)

        # add confirmation code to user profile
        user_profile.sms_activation = confirm_code
        user_profile.save()
        params = {'success': True, 'phone': user_profile.phone_number, 'page_title': 'Confirm code'}
        params.update(csrf(request))

        return render_to_response('confirm.html', params)
    else:
        request.user_profile = user_profile
        request.bypass_confirm_phone = True
        return confirm_reg_code(request)


# Process reg confirmation code
def confirm_reg_code(request):
    confirm_code = request.POST.get('confirm_code', '')

    user_profile = request.user_profile if request.user_profile else get_object_or_404(UserProfile,
                                                                                       sms_activation=confirm_code)
    # check if is correct confirmation code
    if user_profile.sms_activation == confirm_code or request.bypass_confirm_phone:
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
        if not request.bypass_confirm_phone:
            confirmed = "You have successfully confirmed your phone number!"
        else:
            confirmed = "You have successfully registered!"
        confirmed += ' Please log in to continue.'
        return HttpResponseRedirect(reverse('django_auth') + "?reg_success=True&reg_message=" + confirmed)
    else:
        return HttpResponseRedirect(reverse('django_auth.invalid_code'))


# Send SMS
def send_sms(send_to, send_message):
    account = settings.TWILLIO_ACCOUNT
    token = settings.TWILLIO_TOKEN
    client = TwilioRestClient(account, token)

    client.messages.create(to=send_to, from_=settings.TWILLIO_FROM,
                           body=send_message)
    return None
