from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Command(BaseCommand):
    help = 'Verify custom admin URLs'

    def handle(self, *args, **kwargs):
        self.stdout.write('Verifying custom admin URLs...')

        # Ensure admin user exists
        username = 'admin'
        password = 'adminpassword'
        email = 'admin@example.com'
        
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
        except User.DoesNotExist:
            user = User.objects.create_superuser(username=username, email=email, password=password)

        client = Client()
        client.login(username=username, password=password)

        urls_to_check = [
            ('admin_requests_list', 'Requests List'),
            ('admin_request_create', 'Request Create'),
            ('admin_professors_list', 'Professors List'),
            ('admin_professor_create', 'Professor Create'),
            ('admin_classrooms_list', 'Classrooms List'),
            ('admin_classroom_create', 'Classroom Create'),
            ('admin_delegates_list', 'Delegates List'),
            ('admin_delegate_create', 'Delegate Create'),
            ('admin_blog_list', 'Blog List'),
            ('admin_blog_create', 'Blog Create'),
            ('admin_sponsorship_mentees', 'Sponsorship Mentees'),
            ('admin_sponsorship_mentors', 'Sponsorship Mentors'),
            ('admin_sponsorship_matches', 'Sponsorship Matches'),
        ]

        all_passed = True
        for url_name, description in urls_to_check:
            try:
                url = reverse(url_name)
                response = client.get(url)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS(f'[OK] {description} ({url})'))
                else:
                    self.stdout.write(self.style.ERROR(f'[FAIL] {description} ({url}) - Status: {response.status_code}'))
                    all_passed = False
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'[ERROR] {description}: {str(e)}'))
                all_passed = False

        if all_passed:
            self.stdout.write(self.style.SUCCESS('All admin URLs verified successfully!'))
        else:
            self.stdout.write(self.style.ERROR('Some admin URLs failed verification.'))
