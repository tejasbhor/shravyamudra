from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from profiles.models import Profile

class Command(BaseCommand):
    help = 'Robust user management: create, list, promote/demote, and repair user profiles.'

    def add_arguments(self, parser):
        parser.add_argument('--create', nargs=3, metavar=('USERNAME', 'EMAIL', 'PASSWORD'), help='Create a new user')
        parser.add_argument('--role', type=str, help='Role for new user (admin/user)')
        parser.add_argument('--superuser', action='store_true', help='Make user a superuser')
        parser.add_argument('--staff', action='store_true', help='Make user staff')
        parser.add_argument('--list', action='store_true', help='List all users')
        parser.add_argument('--promote', metavar='USERNAME', help='Promote user to admin')
        parser.add_argument('--demote', metavar='USERNAME', help='Demote user to user')
        parser.add_argument('--repair-profiles', action='store_true', help='Repair missing profiles for all users')

    def handle(self, *args, **options):
        User = get_user_model()
        if options['create']:
            username, email, password = options['create']
            role = options['role'] or 'user'
            is_superuser = options['superuser']
            is_staff = options['staff']
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.ERROR(f'User {username} already exists.'))
                return
            user = User.objects.create_user(username=username, email=email, password=password)
            user.role = role
            user.is_superuser = is_superuser
            user.is_staff = is_staff
            user.save()
            Profile.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f'User {username} created with role {role}.'))
        if options['list']:
            for u in User.objects.all():
                self.stdout.write(f'{u.username} | {u.email} | role: {u.role} | superuser: {u.is_superuser} | staff: {u.is_staff}')
        if options['promote']:
            try:
                u = User.objects.get(username=options['promote'])
                u.role = 'admin'
                u.is_superuser = True
                u.is_staff = True
                u.save()
                self.stdout.write(self.style.SUCCESS(f'User {u.username} promoted to admin.'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR('User not found.'))
        if options['demote']:
            try:
                u = User.objects.get(username=options['demote'])
                u.role = 'user'
                u.is_superuser = False
                u.save()
                self.stdout.write(self.style.SUCCESS(f'User {u.username} demoted to user.'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR('User not found.'))
        if options['repair_profiles']:
            repaired = 0
            for u in User.objects.all():
                if not hasattr(u, 'profile'):
                    Profile.objects.create(user=u)
                    repaired += 1
            self.stdout.write(self.style.SUCCESS(f'Repaired {repaired} user profiles.'))
