from django.core.management import BaseCommand

from scans import loader, api_helper
from scans import models


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('publication', nargs='?', type=str)

    def handle(self, *args, **options):
        for issue in models.IssueScan.objects.filter(publication_id=options['publication']).exclude(issuecode=None):
            try:
                issue_info = api_helper.api_request_single('issue', issuecode=issue.issuecode)
            except RuntimeError as e:
                print(e)
                continue

            publication = loader.load_publication(issue_info['publication'])

            loader.load_issue_info(issue.path, publication, issue_info, True)
            pass
