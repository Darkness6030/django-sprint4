"""Статические страницы и обработчики ошибок."""

from django.shortcuts import render
from django.views.generic import TemplateView


class About(TemplateView):
    """Описание проекта."""

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """Правила публикации."""

    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    """Отобразить ошибку проверки CSRF."""
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    """Отобразить страницу отсутствующего ресурса."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Отобразить внутреннюю ошибку сервера."""
    return render(request, 'pages/500.html', status=500)
