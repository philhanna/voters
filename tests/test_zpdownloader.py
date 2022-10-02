import os.path
import filecmp
import subprocess
from unittest import TestCase
from zipfile import ZipFile

from tests import testdata
from voters import ZIP_FILE_NAME, ZipDownloader, TMP, ZIP_CHUNK_SIZE


class TestDownloader(TestCase):

    def test_init(self):
        name, ext = os.path.splitext(ZIP_FILE_NAME)
        self.assertTrue(name.startswith("/tmp"))
        self.assertEqual(ext, ".zip")

    def test_run_file_size(self):
        zipfile = os.path.join(testdata, "ten_voters.zip" )
        app = ZipDownloader(zipfile)
        app.zipfile_size = os.path.getsize(zipfile)
        app.run()
        expected = 1585
        actual = app.zipfile_size
        self.assertEqual(expected, actual)

    def test_run_with_ten_voters(self):

        class ZipLocal(ZipDownloader):
            """Subclass of ZipDownloader that lets me override
            the ``read_chunks`` method so that it reads/writes
            locally with a small file"""

            def __init__(self, source=None, zipfile=None):
                super().__init__(source, zipfile)

            def read_chunks(self):
                """Reads the small zipfile in testdata and returns it in chunks"""
                testzip = os.path.join(testdata, "ten_voters.zip")
                with open(testzip, "rb") as fp:
                    chunk_size = 512
                    while True:
                        chunk = fp.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk

        # The output will be a zip file in /tmp
        zipfile_in_tmp = os.path.join(TMP, "ten_voters.zip")
        if os.path.exists(zipfile_in_tmp):
            os.remove(zipfile_in_tmp)

        app = ZipLocal(zipfile=zipfile_in_tmp)
        app.run()

        # Unzip the generated .zip file
        with ZipFile(zipfile_in_tmp) as myzip:
            myzip.extract("ten_voters.txt", path=TMP)

        file1 = os.path.join(TMP, "ten_voters.txt")
        file2 = os.path.join(testdata, "ten_voters.txt")

        self.assertTrue(filecmp.cmp(file1, file2))
        os.remove(zipfile_in_tmp)
        os.remove(file1)