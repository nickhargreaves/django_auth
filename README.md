=====
Django Auth
=====

Django Auth is a simple app for user authentication with Django. 

It does the following: login/logout, register, email + SMS confirmations with Twilio

##### Quick start

1. Add "django_auth" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        
        'django_auth',
    )

2. Include the django_auth URLconf in your project urls.py like this::

    url(r'^django_auth/', include('django_auth.urls')),
    
3. Install Twilio 

    pip install twilio

4. Add Twilio to your requirements.txt file

5. Go to your settings.py and add your Twilio credentials at the bottom of the file
    ```# Twillio settings
    TWILLIO_ACCOUNT = ''
    TWILLIO_TOKEN = ''
    TWILLIO_FROM = ''
    ```
6. Go to your projects main urls.py and add this to your URL 

    `url(r'^django_auth/', include('django_auth.urls')),`


7. Run `python manage.py migrate` to create the django_auth models.

8. Start the development server and visit http://127.0.0.1:8000/django_auth/
   

##### Demo

You can try out the demo here https://hidden-reef-1355.herokuapp.com/