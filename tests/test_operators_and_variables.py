from io import StringIO
from unittest import TestCase

from py2c_ast import CConverter, main


class Py2CTestCase(TestCase):
    def setUp(self):
        self.file_stdout = StringIO()
        self.converter = CConverter(save_to=self.file_stdout)

    def assertSuccess(self, source_code, result_code):
        main(self.converter, source_code)
        self.assertEqual(self.file_stdout.getvalue(), result_code)

    def assertBad(self, exception, source_code):
        self.assertRaises(exception, main, self.converter, source_code)


class OperatorsAndVariablesTestCase(Py2CTestCase):
    def test_init_empty_variable(self):
        source_code = 'variable: int'
        result_code = 'int variable;\n'
        self.assertSuccess(source_code, result_code)

    def test_init_integer_variable(self):
        source_code = 'variable: int = 1'
        result_code = 'int variable = 1;\n'
        self.assertSuccess(source_code, result_code)

    def test_init_string_variable(self):
        source_code = 'variable: char = \'1\''
        result_code = 'char variable = \"1\";\n'
        self.assertSuccess(source_code, result_code)

    def test_init_string_variable2(self):
        source_code = 'variable: char = \'a\''
        result_code = 'char variable = \"a\";\n'
        self.assertSuccess(source_code, result_code)

    def test_init_integer_variable_with_operators(self):
        source_code = 'variable: int = None'
        result_code = 'int variable = NULL;\n'
        self.assertSuccess(source_code, result_code)

    def test_init_some_variables_with_the_different_types(self):
        source_code = 'a: int\nb: float\nc: char'
        result_code = 'int a;\nfloat b;\nchar c;\n'
        self.assertSuccess(source_code, result_code)

    # def test_init_some_variables_with_the_same_types(self):
    #     source_code = 'a: int\nb: int\nc: int'
    #     result_code = 'int a, b, c;\n'
    #     self.assertSuccess(source_code, result_code)


class UnaryOperatorsTestCase(Py2CTestCase):
    def test_usub(self):
        source_code = 'variable: int = 1\nvariable = -variable'
        result_code = 'int variable = 1;\nvariable = -variable;\n'
        self.assertSuccess(source_code, result_code)

    def test_uadd(self):
        source_code = 'variable: int = 1\nvariable = +variable'
        result_code = 'int variable = 1;\nvariable = +variable;\n'
        self.assertSuccess(source_code, result_code)

    def test_not(self):
        source_code = 'variable: int = 1\nvariable = not variable'
        result_code = 'int variable = 1;\nvariable = !variable;\n'
        self.assertSuccess(source_code, result_code)

    def test_invert(self):
        source_code = 'variable: int = 1\nvariable = ~variable'
        result_code = 'int variable = 1;\nvariable = ~variable;\n'
        self.assertSuccess(source_code, result_code)

