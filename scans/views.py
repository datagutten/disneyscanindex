import re
from pathlib import Path

import django.http
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from sorl.thumbnail import get_thumbnail

from scans import models, api_helper, loader


def _issues_year(request, publication_obj: models.Publication):
    issues_year = {}
    for issue in publication_obj.issues.all():
        if issue.year not in issues_year:
            issues_year[issue.year] = []
        issues_year[issue.year].append(issue)

    return render(request, 'scans/publication.html', {'publication': publication_obj, 'issues_year': issues_year})


def completion(request):
    code = request.GET.get('publicationcode')
    publication_obj = get_object_or_404(models.Publication, publicationcode=code)
    years = publication_obj.issues.values('year').distinct()
    return _issues_year(request, publication_obj)


def publication(request, code=None):
    if not code:
        code = request.GET.get('publicationcode')
        if not code:
            return HttpResponseRedirect(reverse('scans:publications'))
    else:
        code = api_helper.replace_dash(code)
    publication_obj = get_object_or_404(models.Publication, publicationcode=code)
    return _issues_year(request, publication_obj)


def publications(request):
    publications_obj = models.Publication.objects.all()
    return render(request, 'scans/publications.html', {'publications': publications_obj})


def scans(request):
    story = api_helper.api_request('story', request.GET.get('storycode'))
    issues = []
    for issue in story['issuecodes']:
        try:
            issue_scans = models.IssueScan.objects.filter(issuecode=issue)
            for issue_obj in issue_scans:
                if issue_obj.exists():
                    issues.append(request.scheme + '://' + request.get_host() + reverse(
                        'scans:pdf') + '?issuecode=' + issue_obj.issuecode)

        except models.IssueScan.DoesNotExist:
            continue

    return JsonResponse({'issues': issues})


def pdf_proxy(request, scan_id: int = None, file_name=None):
    if scan_id:
        issue_scans = [models.IssueScan.objects.get(pk=scan_id)]
    elif request.GET.get('issuecode'):
        issue_scans = models.IssueScan.objects.filter(issuecode=request.GET.get('issuecode'))
    elif request.GET.get('file'):
        issue_scans = models.IssueScan.objects.filter(file=request.GET.get('file'))
    else:
        return django.http.HttpResponseNotFound('issuecode or file must be set')

    files = []
    for issue_obj in issue_scans:
        file = issue_obj.path
        files.append(file)

        if not file.exists():
            continue
        if file.suffix not in loader.comic_extensions:
            continue

        # if file.suffix != '.pdf':
        #     pdf_file = issue_obj.pdf()
        #     if pdf_file:
        #         file = pdf_file

        with file.open('rb') as fp:
            if file.suffix == '.pdf':
                response = HttpResponse(fp.read(), content_type='application/pdf')
                # Use 'inline' to display in browser, 'attachment' to force download
                response['Content-Disposition'] = 'inline; filename="' + file.name + '"'
            else:
                response = HttpResponse(fp.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = 'filename="' + file.name + '"'

            return response
    return HttpResponseNotFound('File not found ' + '\n'.join(map(str, files)))


def cover(request, issue: str = None):
    if not issue:
        issuecode = request.GET.get('issuecode')
        issue_obj = models.IssueScan.objects.get(issuecode=issuecode)
    else:
        issue_obj = models.IssueScan.objects.get(id=issue)
    image = issue_obj.get_cover()
    geometry = request.GET.get('geometry')
    if geometry:
        im = get_thumbnail(image, geometry)
        url = im.url
    else:
        url = issue_obj.get_cover().url

    return HttpResponseRedirect(url)


def renumber(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('issue_'):
                issue_id = re.sub(r'issue_(\d+)', r'\1', key)
                issue_obj = models.IssueScan.objects.get(id=issue_id)
                if value != issue_obj.issuecode:
                    issue_obj.issuecode = value
                    issue_obj.save()
                pass

    publicationcode = api_helper.replace_dash(request.GET.get('publication'))
    issues = models.IssueScan.objects.filter(publication_id=publicationcode)
    return render(request, 'scans/renumber.html', {'issues': issues.all()})


def _find_comics(path: Path) -> list[Path]:
    comics = []
    for issue_file in path.iterdir():
        if issue_file.is_dir():
            comics += _find_comics(issue_file)
            continue
        if issue_file.suffix not in loader.comic_extensions:
            continue
        if not issue_file.is_file():
            continue
        comics.append(issue_file)
    return comics


def identify(request):
    publicationcode = api_helper.replace_dash(request.GET.get('publication'))
    try:
        publication_obj = models.Publication.objects.get(pk=publicationcode)
    except models.Publication.DoesNotExist:
        try:
            publication_obj = loader.load_publication(publicationcode)
        except RuntimeError:
            publication_obj = None
    # issues = publication_obj.issues.values_list('path', flat=True)

    if request.method == 'POST':
        for key, value in request.POST.items():
            if value == 'None' or value == '':
                continue
            if key.startswith('issue_'):
                issue_id = re.sub(r'issue_(\d+)', r'\1', key)
                issue_obj = models.IssueScan.objects.get(id=issue_id)
                if value != issue_obj.issuecode:
                    # issue_obj.publication = None
                    issue_obj.issuecode = value
                    issue_obj.save()
    if publication_obj:
        known_files = {issue.path: issue.issuecode for issue in publication_obj.issues.all()}
    else:
        known_files = {}
    issues = []
    files = _find_comics(settings.COMICS_ROOT.joinpath(api_helper.replace_slash(publicationcode)))

    for issue_file in files:
        if not issue_file.is_file() or (issue_file in known_files.keys() and known_files[issue_file] is not None):
            continue
        issue_file_rel = issue_file.relative_to(settings.COMICS_ROOT)
        issue_obj, created = models.IssueScan.objects.get_or_create(file=issue_file_rel.as_posix(),
                                                                    defaults={'publication_id': publicationcode})
        if issue_obj.issuecode is not None:
            continue
        issues.append(issue_obj)
    return render(request, 'scans/renumber.html', {'issues': issues, 'publication': publication_obj})


def issue_info(request):
    publicationcode = request.GET.get('publicationcode')
    filename = request.GET.get('filename')
    publication_obj = models.Publication.objects.get(publicationcode=publicationcode)
    issue_obj = loader.identify_issue(Path(filename), publication_obj)
    return JsonResponse(issue_obj)
