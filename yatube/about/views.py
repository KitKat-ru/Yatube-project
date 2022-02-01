from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Представление передающее статичную страницу."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Представление передающее статичную страницу."""
    template_name = 'about/tech.html'
