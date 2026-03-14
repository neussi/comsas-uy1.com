from django.urls import path
from django.http import HttpResponse
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, JuinSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'juin': JuinSitemap,
}

def robots_txt(request):
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /admin_dashboard/
Disallow: /login/
Disallow: /register/

Sitemap: {}://{}/sitemap.xml
""".format(request.scheme, request.get_host())
    return HttpResponse(content, content_type="text/plain")

urlpatterns = [
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
