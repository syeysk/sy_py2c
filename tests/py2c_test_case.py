from io import StringIO
from unittest import TestCase

from py2c import CConverter, main


class Py2CTestCase(TestCase):
    def setUp(self):
        self.file_stdout = StringIO()
        self.converter = CConverter(save_to=self.file_stdout)

    def assertSuccess(self, source_code, result_code):
        main(self.converter, source_code)
        self.assertEqual(self.file_stdout.getvalue(), result_code)

    def assertBad(self, source_code, exception):
        self.assertRaises(exception, main, self.converter, source_code)
