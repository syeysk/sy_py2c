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


class TernaryOperatorTestCase(Py2CTestCase):
    def test_ternary(self):
        source_code = 'a: int = 1\nb: int\nb = 10 if a == 99 else b'
        result_code = 'int a = 1;\nint b;\nb = (a == 99) ? 10 : b;\n'
        self.assertSuccess(source_code, result_code)


class DeleteTestCase(Py2CTestCase):
    def test_delete(self):
        source_code = 'del a, b'
        result_code = 'delete a;\ndelete b;\n'
        self.assertSuccess(source_code, result_code)


class PreprocConstantsTestCase(Py2CTestCase):
    def test_variable(self):
        # TODO: использовать preproc вместо const
        source_code = 'TEST_CONST: preproc = 56'
        result_code = '#define TEST_CONST 56\n'
        #self.assertSuccess(source_code, result_code)

    def test_function(self):
        # TODO: использовать preproc вместо const
        source_code = 'TEST_FUNC: preproc = lambda x, y: x-y*7'
        # TODO: убрать пробел между `TEST_FUNC` и `(x,y)`
        result_code = '#define TEST_FUNC (x,y) x - (y * 7)\n'
        #result_code = '#define TEST_FUNC(x,y) x - (y * 7)\n'
        #self.assertSuccess(source_code, result_code)


class ImportTestCase(Py2CTestCase):
    def test_import_one_module(self):
        source_code = 'import module1'
        result_code = '#include <module1.h>\n\n'
        self.assertSuccess(source_code, result_code)

    def test_import_some_modules_inline(self):
        source_code = 'import module1, module2, module3'
        result_code = '#include <module1.h>\n#include <module2.h>\n#include <module3.h>\n\n'
        self.assertSuccess(source_code, result_code)

    def test_import_some_modules_multiline(self):
        source_code = 'import module1\nimport module2\nimport module3'
        # TODO: убрать двойные пробелы между импортами
        result_code = '#include <module1.h>\n\n#include <module2.h>\n\n#include <module3.h>\n\n'
        self.assertSuccess(source_code, result_code)

    def test_import_from(self):
        source_code = 'from module1 import name1, name2'
        result_code = '#include <module1.h>\n\n'
        self.assertSuccess(source_code, result_code)

    def test_import_from_multi(self):
        source_code = 'from module1 import name1, name2\nfrom module2 import name3, name4'
        result_code = '#include <module1.h>\n\n#include <module2.h>\n\n'
        self.assertSuccess(source_code, result_code)


class FunctionTestCase(Py2CTestCase):
    # def test_empty_function(self):
    #     source_code = 'def function() -> None: pass'
    #     result_code = 'void function(void) {\n}\n'
    #     self.assertSuccess(source_code, result_code)

    def test_empty_typed_function(self):
        source_code = 'def function() -> int: pass'
        result_code = 'int function(void) {\n}\n'
        self.assertSuccess(source_code, result_code)

    def test_typed_function_with_return(self):
        source_code = 'def function() -> int: return 34'
        result_code = 'int function(void) {\n    return 34;\n}\n'
        self.assertSuccess(source_code, result_code)

    def test_typed_function_with_return_and_args(self):
        source_code = 'def function(arg1: float, arg2: char) -> int:\n    a: int = 5\n    return a + arg1'
        result_code = 'int function(float arg1, char arg2) {\n    int a = 5;\n    return a + arg1;\n}\n'
        self.assertSuccess(source_code, result_code)

    # def test_typed_function_with_return_none(self):
    #     source_code = 'def function() -> None: return'
    #     result_code = 'void function(void) {\n    return;\n}\n'
    #     self.assertSuccess(source_code, result_code)

    # def test_typed_function_with_return_none(self):
    #     source_code = 'def function() -> None: return None'
    #     result_code = 'void function(void) {\n    return NULL;\n}\n'
    #     self.assertSuccess(source_code, result_code)

    def test_calling_function(self):
        source_code = 'function(arg1, 1)'
        result_code = 'function(arg1, 1);\n'
        self.assertSuccess(source_code, result_code)

    def test_assign_calling_function(self):
        source_code = 'variable: int = function(arg1, 1)'
        result_code = 'int variable = function(arg1, 1);\n'
        self.assertSuccess(source_code, result_code)

    def test_assign_calling_function_with_ternary_op(self):
        source_code = 'variable: int = function(arg1, 5 if c > 45 else d)'
        result_code = 'int variable = function(arg1, ((c > 45) ? 5 : d));\n'
        self.assertSuccess(source_code, result_code)


class IfTestCase(Py2CTestCase):
    def test_if(self):
        source_code = 'if variable > 1:\n    variable2 = 2'
        result_code = 'if (variable > 1) {\n    variable2 = 2;\n}\n\n'
        self.assertSuccess(source_code, result_code)

    def test_if_else(self):
        source_code = 'if variable > 1:\n    variable2 = 2\nelse:\n    variable3 = 3'
        result_code = 'if (variable > 1) {\n    variable2 = 2;\n} else {\n    variable3 = 3;\n}\n\n'
        self.assertSuccess(source_code, result_code)
