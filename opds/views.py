from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from scans import models
from scans import api_helper
from . import opds


def publications(request):
    feed = opds.OPDS('Publications', 'disneyscanindex')
    for publication_obj in models.Publication.objects.exclude(issues=None):
        entry = feed.entry(publication_obj.title, publication_obj.pk)
        entry.navigation(reverse('opds:publication', kwargs={'code': api_helper.replace_slash(publication_obj.pk)}))

    return HttpResponse(feed.render(), content_type='text/xml')


def publication_by_year(request, code: str, year=None):
    code = api_helper.replace_dash(code)
    publication_obj = get_object_or_404(models.Publication, pk=code)
    feed = opds.OPDS(publication_obj.title, 'disneyscanindex')
    years = publication_obj.issues.order_by().values('year').distinct()
    for year_iter in years:
        if year_iter['year'] is None:
            continue

        issues = publication_obj.issues.filter(year=year_iter['year']).exclude(issuecode=None)
        entry = feed.entry('%d' % year_iter['year'], '%s-%d' % (publication_obj.pk, year_iter['year']))
        url_args = {'code': api_helper.replace_slash(publication_obj.pk), 'year': year_iter['year']}
        entry.navigation(reverse('opds:publication', kwargs=url_args))

    return HttpResponse(feed.render(), content_type='text/xml')
    pass


def publication(request, code: str, year=None):
    code = api_helper.replace_dash(code)
    publication_obj = get_object_or_404(models.Publication, pk=code)
    feed = opds.OPDS(publication_obj.title, 'disneyscanindex')
    if publication_obj.issues.count() > 50 and not year:
        return publication_by_year(request, code)
    elif year is not None:
        issues = publication_obj.issues.exclude(issuecode=None).filter(year=year)
    else:
        issues = publication_obj.issues.exclude(issuecode=None)

    for issue_obj in issues:
        scan = issue_obj
        # entry = feed.entry(issue_obj.title or issue_obj.issuecode, issue_obj.issuecode)
        # entry.navigation(reverse('opds:issue', kwargs={'code': issue_obj.issuecode_dash}))

        entry = feed.entry(scan.path.name, str(scan.pk))
        cover = reverse('scans:cover', kwargs={'issue': scan.pk})
        entry.content(scan.title)
        entry.content_link(cover, 'image/jpeg', 'http://opds-spec.org/image')

        if scan.path.suffix == '.pdf':
            content_type = 'application/pdf'
        # elif scan.path.suffix in ['.cbz', '.cbr']:
        #     content_type = 'application/x-cdisplay'
        else:
            content_type = 'application/octet-stream'

        entry.content_link(reverse('scans:file', kwargs={'scan_id': scan.pk, 'file_name': scan.path.name}),
                           content_type,
                           'http://opds-spec.org/acquisition')

    return HttpResponse(feed.render(), content_type='text/xml')


def issue(request, code: str):
    code = api_helper.replace_dash(code)
    feed = opds.OPDS(code, 'disneyscanindex')
    for scan in models.IssueScan.objects.filter(issuecode=code):
        entry = feed.entry(scan.path.name, str(scan.pk))
        cover = reverse('scans:cover', kwargs={'issue': scan.pk})
        entry.content_link(cover, 'image/jpeg', 'http://opds-spec.org/image')
        if scan.path.suffix == '.pdf':
            content_type = 'application/pdf'
        # elif scan.path.suffix in ['.cbz', '.cbr']:
        #     content_type = 'application/x-cdisplay'
        else:
            content_type = 'application/octet-stream'

        entry.content_link(reverse('scans:file', kwargs={'scan_id': scan.pk, 'file_name': scan.path.name}),
                           content_type,
                           'http://opds-spec.org/acquisition')

    return HttpResponse(feed.render(), content_type='text/xml')
