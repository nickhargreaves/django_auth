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

    `url(r'^your-chosen-path/', include('django_auth.urls')),`
    
3. Install Twilio 

    `pip install twilio`

4. Add Twilio to your requirements.txt file

5. Go to your settings.py and add your Twilio credentials at the bottom of the file

    ```
    # Twillio settings
    TWILLIO_ACCOUNT = ''
    TWILLIO_TOKEN = ''
    TWILLIO_FROM = ''
    ```
6. Add the following settings as well:
    ```
    REQUIRE_PHONE_VERIFICATION_ON_LOGIN = False # Set to true to enable Two-Factor Authentication
    REQUIRE_PHONE_VERIFICATION_ON_REGISTER = False # Set to true if you want users to confirm phone number
    FROM_EMAIL_ADDRESS = "The email address to show as source of your confirmation address"
    ```

6. Run `python manage.py migrate` to create the django_auth models.


7. Start the development server and visit http://127.0.0.1:8000/django_auth/
   

##### Demo

You can try out the demo here https://hidden-reef-1355.herokuapp.com/