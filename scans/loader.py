import re
from pathlib import Path

from disneyscanindex import settings
from scans import folder_mappings, models, api_helper

comic_extensions = ['.pdf', '.cbr', '.cbz']


def find_issue(publication: models.Publication, num: int, year: int):
    numbers = []
    if year:
        numbers.append('%s-%s' % (str(year), str(num)))
        numbers.append('%s-%d' % (str(year), int(num)))  # Strip leading zeroes
        numbers.append('%s-%02d' % (str(year), int(num)))  # Add leading zero

    numbers.append(str(num))
    try:
        numbers.append(str(int(num)))  # Strip leading zeroes
    except ValueError:
        pass
    # Remove duplicate numbers
    [numbers.pop(idx) for idx, elem in enumerate(numbers) if numbers.count(elem) != 1]

    for number in numbers:
        try:
            return api_helper.api_request_single('issue', publication_id=publication.pk, issuenumber=number)
        except RuntimeError as e:
            continue
    raise RuntimeError('%s: Issue not found, tried the following codes: "%s"' % (publication, ', '.join(numbers)))


def get_issue_number(file: Path, publication: models.Publication):
    file_name = file.name
    if publication.pk in folder_mappings.issuecode:
        matches = folder_mappings.issuecode[publication.pk].search(file.name)
        if matches:
            if len(matches.groups()) == 1:
                return None, matches.group(1)
            else:
                pass

    matches_year = re.search(r'([12]\d{3}).*?[\s_-](\d+)', file_name)
    if matches_year:
        return matches_year.group(1), matches_year.group(2)

    matches = re.search(r'%s\s?([\d-]+)' % publication.title, file_name)
    if matches:
        return None, matches.group(1)

    matches_volume = re.search(r'v\d+ (\d+).+?([12]\d{3})', file_name)
    if matches_volume:
        return matches_volume.group(2), matches_volume.group(1)

    matches_year_reverse_single_sep = re.search(r'(\d+).([12]\d{3})', file_name)
    if matches_year_reverse_single_sep:
        return matches_year_reverse_single_sep.group(2), matches_year_reverse_single_sep.group(1)

    matches_year_reverse = re.search(r'(\d+).+\(([12]\d{3})\)', file_name)
    if matches_year_reverse:
        return matches_year_reverse.group(2), matches_year_reverse.group(1)

    matches_number = re.search(r'%s (\d+)' % publication.title, file_name)
    if matches_number:
        return None, matches_number.group(1)

    # Matches a number surrounded by spaces or a non-digit to avoid matching years
    matches_num_only = re.search(r'(?:^|\s)(\d{1,3})[\s.]', file_name)
    if matches_num_only:
        return None, matches_num_only.group(1)

    return None, None


def identify_issue(file: Path, publication: models.Publication):
    year, num = get_issue_number(file, publication)
    if not year and not num:
        raise RuntimeError('Unable to parse issue number from "%s"' % file.name)
    return find_issue(publication, num, year)


def load_issue_info(file: Path, publication: models.Publication, issue: dict, update=False) -> models.IssueScan:
    if file.suffix not in comic_extensions:
        raise RuntimeError("Unknown file extension %s" % file.suffix)
    try:
        file_rel = file.relative_to(settings.COMICS_ROOT).as_posix()
    except ValueError:
        file_rel = file

    fields = {
        'publication': publication,
        'issuecode': issue['issuecode'],
        'title': issue['full_title'],
        'year': issue['year'],
        'file': file_rel
    }

    if not update:
        scan_obj, created = models.IssueScan.objects.get_or_create(file=file_rel, defaults=fields)
    else:
        scan_obj, created = models.IssueScan.objects.update_or_create(file=file_rel, defaults=fields)
        pass

    return scan_obj


def load_publication(publication_code: str) -> models.Publication:
    publication = api_helper.api_request_single('publication',
                                                publicationcode=api_helper.replace_dash(publication_code))

    # publication_obj = models.Publication(publicationcode=publication_code,
    #                                      title=publication['title'])
    publication_obj, created = models.Publication.objects.get_or_create(publicationcode=publication_code,
                                                                        defaults={'title': publication['title']})
    return publication_obj
