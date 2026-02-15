import zipfile
from pathlib import Path
from typing import List

import rarfile

image_extensions = ['.jpg', '.png', '.jpeg']


class Cover:
    def __init__(self, file: Path):
        self.path = file
        self.open()

    def open(self):
        raise NotImplementedError

    def get_files(self) -> List[Path]:
        raise NotImplementedError

    def first_page(self) -> Path:
        files = self.get_files()
        files.sort()
        for file in files:
            if file.suffix in image_extensions:
                return file
        raise FileNotFoundError('No image file found')


class ArchiveCover(Cover):
    fp = None

    def get_files(self) -> List[Path]:
        return [Path(file) for file in self.fp.namelist()]

    def get_file(self, file: Path):
        return self.fp.open(file.as_posix())

    def extract(self, member: Path, path: Path = None, pwd=None):
        file = self.fp.extract(str(member), path=path, pwd=pwd)
        if path:
            return path.parent.joinpath(file)
        else:
            return Path(file)

    def close(self):
        self.fp.close()


class ZipCover(ArchiveCover):
    fp: zipfile.ZipFile

    def open(self):
        try:
            self.fp = zipfile.ZipFile(self.path)
        except zipfile.BadZipFile as e:
            raise RuntimeError(e) from e


class RarCover(ArchiveCover):
    fp: rarfile.RarFile

    def open(self):
        try:
            self.fp = rarfile.RarFile(self.path)
        except rarfile.Error as e:
            raise RuntimeError(e)
