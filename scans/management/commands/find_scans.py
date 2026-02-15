from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand

from scans import api_helper
from scans import loader
from scans import models


class Command(BaseCommand):
    publication: dict
    publication_name: str
    publication_obj: models.Publication

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.publication_obj = None

    def add_arguments(self, parser):
        parser.add_argument('folder', nargs='?', type=str)
        parser.add_argument('recheck', nargs='?', type=str)

    def scan_folder(self, folder: Path, publication_code: str = None, recheck: str = None):
        for issue_file in folder.iterdir():
            if issue_file.is_dir():
                self.scan_folder(issue_file, publication_code, recheck)
                continue
            if issue_file.suffix not in loader.comic_extensions:
                continue
            try:
                issue_file_rel = issue_file.relative_to(settings.COMICS_ROOT)
            except ValueError:
                issue_file_rel = issue_file

            if recheck is None or recheck != publication_code:
                try:
                    models.IssueScan.objects.get(file=issue_file_rel.as_posix())
                    continue
                except models.IssueScan.DoesNotExist:
                    pass

            try:
                issue = loader.identify_issue(issue_file, self.publication_obj)
            except RuntimeError as e:
                models.IssueScan.objects.get_or_create(file=issue_file_rel.as_posix(),
                                                       defaults={'publication': self.publication_obj})
                print(e, issue_file.name)
                continue
            try:
                scan_obj = loader.load_issue_info(issue_file, self.publication_obj, issue)
            except RuntimeError as e:
                print('%s: %s' % (issue_file.name, e))

            pass

    def handle(self, *args, **options):
        if 'folder' not in options or not options['folder']:
            folder = settings.COMICS_ROOT
        else:
            folder = Path(options['folder'])

        for file in folder.iterdir():
            if not file.is_dir():
                continue

            publication_code = api_helper.replace_dash(file.name)

            try:
                self.publication_obj = loader.load_publication(publication_code)
            except RuntimeError as e:
                print(e)
                continue

            self.scan_folder(file, publication_code, options['recheck'])
