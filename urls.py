from django.conf.urls import url

import django_auth.views

urlpatterns = [
    url(r'^$', django_auth.views.index, name='index'),
    url(r'^login/$', django_auth.views.login),
    url(r'^auth/$', django_auth.views.dj_auth),
    url(r'^profile/$', django_auth.views.profile),
    url(r'^invalid/$', django_auth.views.invalid),
    url(r'^logout/$', django_auth.views.logout),
    url(r'^register/$', django_auth.views.register_user),
    url(r'^register_success/$', django_auth.views.register_success),
    url(r'^confirm/$', django_auth.views.confirm),
]