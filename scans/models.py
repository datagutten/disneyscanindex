import os
import re
from io import BytesIO
from pathlib import Path

from PIL import Image
from django.core.files import File
from django.db import models
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from sorl.thumbnail import ImageField, get_thumbnail
from pdf2image import convert_from_path, convert_from_bytes
from zipfile import ZipFile
import rarfile
from scans import thumbnail, api_helper


# Create your models here.

class Publication(models.Model):
    publicationcode = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title or self.publicationcode

    @property
    def code_dash(self):
        return re.sub(r'([a-z]+)/(.+)', r'\1-\2', self.publicationcode)

    @staticmethod
    def convert_code(publicationcode):
        return re.sub(r'([a-z]+)-(.+)', r'\1/\2', publicationcode)

    def api_url(self):
        return settings.INDUCKS_API + 'publication/' + self.code_dash


class IssueScan(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='issues')
    issuecode = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    file = models.CharField(max_length=200, unique=True)
    year = models.IntegerField(null=True, blank=True)
    cover = ImageField(upload_to='cover', null=True, blank=True)

    class Meta:
        ordering = ['publication', 'issuecode']

    @property
    def issuecode_dash(self):
        return api_helper.replace_slash(self.issuecode)
        # return re.sub(r'([a-z]+)/(.+)', r'\1-\2', self.issuecode)

    def exists(self):
        return self.path.exists()

    def __str__(self):
        if self.title:
            return self.title
        else:
            return '%s %s' % (self.publication, self.issuecode)

    def api_url(self):
        return settings.INDUCKS_API + 'issue/' + self.issuecode_dash

    @property
    def path(self) -> Path:
        path_db = Path(self.file)
        if path_db.is_absolute():
            return path_db
        return settings.COMICS_ROOT.joinpath(path_db.as_posix())

    def get_cover(self):
        if self.cover and os.path.exists(self.cover.path):
            return self.cover
        if self.path.suffix == '.pdf':
            if os.getenv('POPPLER_PATH'):
                poppler = os.getenv('POPPLER_PATH')
            else:
                poppler = None
            images = convert_from_path(str(self.path), first_page=1, last_page=1, fmt='jpeg', poppler_path=poppler)
            fp = BytesIO()
            images[0].save(fp=fp, format='jpeg')
            self.cover = File(fp, self.path.name + '.jpg')
            self.save()
            fp.close()
            return self.cover
        elif self.path.suffix == '.cbz':
            cover_gen = thumbnail.ZipCover(self.path)
        elif self.path.suffix == '.cbr':
            cover_gen = thumbnail.RarCover(self.path)
        else:
            return HttpResponseNotFound('Unable to get cover for extension %s' % self.path.suffix)

        path = cover_gen.first_page()
        self.cover = File(cover_gen.get_file(path), path.name)
        self.save()
        cover_gen.close()
        return self.cover

    def file_url(self):
        return 'http://127.0.0.1:8001/pdf?file=' + self.file

    def pdf(self):
        if self.path.suffix == '.pdf':
            return self.path
        from scans import file_converter
        pdf_file = Path(settings.MEDIA_ROOT).joinpath(self.path.name).with_suffix('.pdf')
        if pdf_file.exists():
            return pdf_file
        elif self.path.suffix == '.cbz':
            return file_converter.cbz_to_pdf(self.path, pdf_file)
        else:
            return None


class StoryScan(models.Model):
    storycode = models.CharField(max_length=100)
    title = models.CharField(max_length=100, null=True, blank=True)
    file = models.CharField(max_length=200, unique=True)

    def exists(self):
        return os.path.exists(self.file)
