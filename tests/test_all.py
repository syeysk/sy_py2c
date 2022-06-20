from io import StringIO
from unittest import TestCase

from py2c import CConverter, main, InvalidAnnotationException, NoneIsNotAllowedException


class Py2CTestCase(TestCase):
    def setUp(self):
        self.file_stdout = StringIO()
        self.converter = CConverter(save_to=self.file_stdout)

    def assertSuccess(self, source_code, result_code):
        main(self.converter, source_code)
        self.assertEqual(self.file_stdout.getvalue(), result_code)

    def assertBad(self, source_code, exception):
        self.assertRaises(exception, main, self.converter, source_code)


class OperatorsAndVariablesTestCase(Py2CTestCase):
    def test_init_variables_with_valid_annotation(self):
        source_code = 'variable1: \'int\' = 1\nvariable2: int = 1'
        result_code = 'int variable1 = 1;\nint variable2 = 1;\n'
        self.assertSuccess(source_code, result_code)

    def test_init_variables_with_invalid_annotation_1(self):
        self.assertBad('a: a + b = 1', InvalidAnnotationException)

    def test_init_variables_with_invalid_annotation_2(self):
        self.assertBad('b: print(1) = 1', InvalidAnnotationException)

    def test_init_empty_variables(self):
        source_code = 'variable1: int'
        result_code = 'int variable1;\n'
        self.assertSuccess(source_code, result_code)

    def test_init_string_variable(self):
        source_code = 'variable: char = \'1\''
        result_code = 'char variable = \"1\";\n'
        self.assertSuccess(source_code, result_code)

    def test_init_string_variable2(self):
        source_code = 'variable: char = \'a\''
        result_code = 'char variable = \"a\";\n'
        self.assertSuccess(source_code, result_code)

    def test_init_some_variables_with_the_different_types(self):
        source_code = 'a: int\nb: float\nc: char'
        result_code = 'int a;\nfloat b;\nchar c;\n'
        self.assertSuccess(source_code, result_code)

    # def test_init_some_variables_with_the_same_types(self):
    #     source_code = 'a: int\nb: int\nc: int'
    #     result_code = 'int a, b, c;\n'
    #     self.assertSuccess(source_code, result_code)


class NoneTestCase(Py2CTestCase):
    def test_none_value_of_variable(self):
        self.assertBad('variable2: int = None', NoneIsNotAllowedException)

    def test_none_annotation_of_variable(self):
        self.assertBad('variable2: None = 1', NoneIsNotAllowedException)

    def test_none_annotation_of_function(self):
        self.assertBad('def function() -> None:\n    pass', NoneIsNotAllowedException)

    def test_typed_function_with_return_none(self):
        self.assertBad('def function(): return None', NoneIsNotAllowedException)


class NULLTestCase(Py2CTestCase):
    ...


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
    def test_variable_preproc(self):
        source_code = 'TEST_CONST: preproc = 56'
        result_code = '#define TEST_CONST 56\n'
        self.assertSuccess(source_code, result_code)

    def test_function(self):
        source_code = 'TEST_FUNC: preproc = lambda x, y: x-y*7'
        result_code = '#define TEST_FUNC(x,y) x - (y * 7)\n'
        self.assertSuccess(source_code, result_code)


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
    def test_empty_function(self):
        source_code = 'def function(): pass'
        result_code = 'void function(void) {\n}\n'
        self.assertSuccess(source_code, result_code)

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

    def test_typed_function_with_return_none(self):
        source_code = 'def function(): return'
        result_code = 'void function(void) {\n    return;\n}\n'
        self.assertSuccess(source_code, result_code)

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

    def test_if_elif_else(self):
        source_code = (
            'if var > 1:\n'
            '    var2 = 2\n'
            'elif var < -10:\n'
            '    var4 = 4\n'
            'elif var < -5:\n'
            '    var5 = 5\n'
            'else:\n'
            '    var3 = 3'
        )
        result_code = (
            'if (var > 1) {\n'
            '    var2 = 2;\n'
            '} else if (var < -10) {\n'
            '    var4 = 4;\n'
            '} else if (var < -5) {\n'
            '    var5 = 5;\n'
            '} else {\n'
            '    var3 = 3;\n'
            '}\n\n'
        )
        self.assertSuccess(source_code, result_code)


class WhileTestCase(Py2CTestCase):
    def test_while(self):
        source_code = (
            'while variable < 10:\n'
            '    variable2 += 1\n'
            '    if variable2 == 0:\n'
            '        break\n'
            '    else:\n'
            '        continue'
        )
        result_code = (
            'while (variable < 10) {\n'
            '    variable2 += 1;\n'
            '    if (variable2 == 0) {\n'
            '        break;\n'
            '    } else {\n'
            '        continue;\n'
            '    }\n\n'  # TODO: должен быть только один перенос
            '}\n\n'
        )
        self.assertSuccess(source_code, result_code)

    def test_while_else(self):
        source_code = (
            'while variable < 10:\n'
            '    variable2 += 1\n'
            '    if variable2 == 0:\n'
            '        break\n'
            '    else:\n'
            '        continue\n'
            'else:\n'
            '   variable = 0'
        )
        result_code = (
            'unsigned byte success = 1;\n'
            'while (variable < 10) {\n'
            '    variable2 += 1;\n'
            '    if (variable2 == 0) {\n'
            '        success = 0;\n'
            '        break;\n'
            '    } else {\n'
            '        continue;\n'
            '    }\n\n'  # TODO: должен быть только один перенос
            '}\n\n'
            'if (success == 1) {\n'
            '    variable = 0;\n'
            '}\n\n'
        )
        self.assertSuccess(source_code, result_code)


class CommentTestCase(Py2CTestCase):
    def test_function_docstring(self):
        source_code = (
            'def function():\n'
            '    """ test docstring"""\n'
        )
        result_code = (
            '\n/*\ntest docstring\n*/\n'
            'void function(void) {\n}\n'
        )
        self.assertSuccess(source_code, result_code)
