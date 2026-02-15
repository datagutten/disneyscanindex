import requests
from django.core.management import BaseCommand

from scans import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        for issue in models.IssueScan.objects.exclude(issuecode=None).filter(year=None):
            print(issue)
            response = requests.get(issue.api_url())
            data = response.json()
            if response.status_code == 404:
                print(data)
                continue

            if 'year' in data:
                issue.year = data['year']
            if 'full_title' in data:
                issue.title = data['full_title']
            else:
                pass
            issue.save()
