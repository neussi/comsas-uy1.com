from django.core.management.base import BaseCommand
from django.test import Client
from main.models import BlogArticle, Contest
from django.urls import reverse

class Command(BaseCommand):
    help = 'Verify public URLs'

    def handle(self, *args, **kwargs):
        self.stdout.write('Verifying public URLs...')
        client = Client()

        # Check Blog List
        try:
            url = reverse('blog_list')
            response = client.get(url)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS(f'[OK] Blog List ({url})'))
            else:
                self.stdout.write(self.style.ERROR(f'[FAIL] Blog List ({url}) - Status: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Blog List: {str(e)}'))

        # Check Blog Detail for the problematic article
        try:
            # Test specific problematic slug
            article = BlogArticle.objects.filter(slug='tuto-déployer-django-sur-vps').first() or BlogArticle.objects.first()
            
            if article:
                url = reverse('blog_detail', args=[article.slug])
                self.stdout.write(f'Testing article slug: {article.slug}')
                response = client.get(url)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f'[OK] Blog Detail ({url})'))
                else:
                    self.stdout.write(self.style.ERROR(f'[FAIL] Blog Detail ({url}) - Status: {response.status_code}'))
            else:
                self.stdout.write(self.style.WARNING('No articles found to test detail view.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Blog Detail: {str(e)}'))

        # Check Requests
        try:
            url = reverse('request_documents')
            response = client.get(url)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS(f'[OK] Requests List ({url})'))
            else:
                self.stdout.write(self.style.ERROR(f'[FAIL] Requests List ({url}) - Status: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Requests: {str(e)}'))

        # Check Department
        dept_urls = ['department_professors', 'department_classrooms', 'department_delegates']
        for url_name in dept_urls:
            try:
                url = reverse(url_name)
                response = client.get(url)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f'[OK] {url_name} ({url})'))
                else:
                    self.stdout.write(self.style.ERROR(f'[FAIL] {url_name} ({url}) - Status: {response.status_code}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'[ERROR] {url_name}: {str(e)}'))

        # Check Blog Like (AJAX)
        try:
            article = BlogArticle.objects.first()
            if article:
                url = reverse('like_article', args=[article.slug])
                response = client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                # It might return 200 JSON
                if response.status_code == 200:
                   import json
                   data = json.loads(response.content)
                   if data.get('success'):
                       self.stdout.write(self.style.SUCCESS(f'[OK] Blog Like ({url}) - Liked! New count: {data.get("likes_count")}'))
                   else:
                       # Could be "already liked" if run multiple times, which is also a success for the endpoint existing
                       self.stdout.write(self.style.SUCCESS(f'[OK] Blog Like ({url}) - Response: {data.get("error")}'))
                else:
                    self.stdout.write(self.style.ERROR(f'[FAIL] Blog Like ({url}) - Status: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Blog Like: {str(e)}'))

        # Check Contests
        try:
            url = reverse('contest_list')
            response = client.get(url)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS(f'[OK] Contest List ({url})'))
            else:
                self.stdout.write(self.style.ERROR(f'[FAIL] Contest List ({url}) - Status: {response.status_code}'))

            # Check Contest Detail
            contest = Contest.objects.first()
            if contest:
                url = reverse('contest_detail', args=[contest.slug])
                response = client.get(url)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f'[OK] Contest Detail ({url})'))
                else:
                    self.stdout.write(self.style.ERROR(f'[FAIL] Contest Detail ({url}) - Status: {response.status_code}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Contests: {str(e)}'))
