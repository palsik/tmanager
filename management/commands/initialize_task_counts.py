# myapp/management/commands/initialize_task_counts.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.home.models import *

class Command(BaseCommand):
    help = 'Initialize task assignment counts for all personnel'

    def handle(self, *args, **kwargs):
        personnel = User.objects.filter(profile1__user_type='personnel')
        for person in personnel:
            TaskAssignmentCount.objects.get_or_create(personnel=person)
        self.stdout.write(self.style.SUCCESS('Successfully initialized task assignment counts'))

