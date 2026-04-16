from django.shortcuts import render

def login(request):
    return render(request, 'core/login.html')


def signup(request):
    return render(request, 'core/register.html')


def profile(request):
    return render(request, 'core/profile.html')