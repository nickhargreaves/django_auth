from django.http import HttpResponse

def index(request):
    return HttpResponse("Not allowed here!")
def login(request):
    return HttpResponse("Login screen")