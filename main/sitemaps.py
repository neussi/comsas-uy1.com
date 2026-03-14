from django.contrib import sitemaps
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'events', 'news', 'projects', 'juin', 'contact']

    def location(self, item):
        return reverse(item)

class JuinSitemap(sitemaps.Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['juin', 'juin_activities', 'juin_commissions', 'juin_sponsors', 'juin_guide']

    def location(self, item):
        return reverse(item)
