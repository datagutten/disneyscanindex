import subprocess
import sys
from pathlib import Path

from PIL import Image

from . import thumbnail


def image_to_pdf(file: Path) -> Path:
    pdf_file = file.with_suffix('.pdf')
    if not pdf_file.exists():
        with file.open("rb") as fp:
            im = Image.open(fp)
            with pdf_file.open("wb") as fp_write:
                im.save(fp_write)
    return pdf_file


def combine_pdf(files: list[Path], output_file: Path) -> Path:
    cmd = ['pdftk'] + [str(file) for file in files] + ['cat', 'output', str(output_file)]
    process = subprocess.run(cmd)
    process.check_returncode()
    for file in files:
        file.unlink()
    return output_file


def cbz_to_pdf(file: Path, pdf_file: Path):
    archive = thumbnail.ZipCover(file)
    extract_folder = pdf_file.parent.joinpath('extract %s' % file.name)
    extract_folder.mkdir(parents=True, exist_ok=True)
    pdf_pages = []
    for file in archive.get_files():
        extracted_file = extract_folder.joinpath(file)
        if not extracted_file.exists():
            extracted = archive.extract(file, extract_folder)
        pdf = image_to_pdf(extracted_file)
        extracted_file.unlink()
        pdf_pages.append(pdf)
    # extract_folder.rmdir()
    pdf_pages.sort()
    return combine_pdf(pdf_pages, pdf_file)


if __name__ == '__main__':
    input_file = Path(sys.argv[1])
    cbz_to_pdf(input_file, input_file.with_suffix('.pdf'))
