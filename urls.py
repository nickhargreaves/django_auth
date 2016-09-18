from django.conf.urls import url

import django_auth.views

urlpatterns = [
    url(r'^$', django_auth.views.index, name='django_auth'),
    url(r'^login/$', django_auth.views.index, name='django_auth.login'),
    url(r'^auth/$', django_auth.views.dj_auth, name='django_auth.auth'),
    url(r'^invalid/$', django_auth.views.invalid, name='django_auth.invalid'),
    url(r'^logout/$', django_auth.views.logout, name='django_auth.logout'),
    url(r'^register/$', django_auth.views.register_user, name='django_auth.register'),
    url(r'^register_success/$', django_auth.views.register_success, name='django_auth.register_success'),
    url(r'^confirm/(?P<activation_key>\w+)/$', django_auth.views.confirm, name='django_auth.confirm'),
    url(r'^confirm_reg_code/$', django_auth.views.confirm_reg_code, name='django_auth.confirm_reg_code'),
    url(r'^confirm_login_code/$', django_auth.views.confirm_login_code, name='django_auth.confirm_login_code')
]