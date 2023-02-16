from io import StringIO
from unittest import TestCase

from py2c.bytecode_walker import translate
from py2c.translator_c import TranslatorC


class Py2CTestCase(TestCase):
    def setUp(self):
        self.file_stdout = StringIO()
        self.translator = TranslatorC(save_to=self.file_stdout)

    def assertSuccess(self, source_code, result_code):
        translate(self.translator, source_code)
        self.assertEqual(self.file_stdout.getvalue(), result_code)

    def assertBad(self, source_code, exception):
        self.assertRaises(exception, translate, self.translator, source_code)
