from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, ProfileForm, SignupForm


def _safe_next_url(request, candidate, fallback_url_name='index'):
    if candidate and url_has_allowed_host_and_scheme(
        url=candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return reverse(fallback_url_name)


def login(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.user.is_authenticated:
        return redirect(_safe_next_url(request, next_url))

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(_safe_next_url(request, next_url))
    else:
        form = LoginForm(request=request)

    return render(request, 'core/login.html', {'form': form, 'next': next_url})


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
    else:
        form = SignupForm()

    return render(request, 'core/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'core/profile.html', {'form': form})


@require_POST
def logout(request):
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    redirect_url = _safe_next_url(request, next_url)
    auth_logout(request)
    return redirect(redirect_url)


def error_403(request, exception=None):
    """Обработчик ошибки 403 Forbidden"""
    return render(request, '403.html', status=403)


def error_404(request, exception=None):
    """Обработчик ошибки 404 Not Found"""
    return render(request, '404.html', status=404)


def error_500(request):
    """Обработчик ошибки 500 Internal Server Error"""
    return render(request, '500.html', status=500)