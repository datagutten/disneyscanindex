import shutil

from django.core.management import BaseCommand

from scans import models


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('publication', nargs='?', type=str)

    def handle(self, *args, **options):
        for issue in models.IssueScan.objects.filter(publication_id=options['publication']).exclude(issuecode=None):
            cover = issue.get_cover()
            shutil.copy(cover.path, issue.path.with_suffix('.jpg'))
