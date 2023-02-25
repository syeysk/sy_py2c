import unittest

from py2c.exceptions import (
    InvalidAnnotationException,
    NoneIsNotAllowedException,
    UnsupportedImportException,
)
from tests.py2c_test_case import Py2CTestCase


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
    def test_invalid_import_one_module(self):
        source_code = 'import module1'
        self.assertBad(source_code, UnsupportedImportException)

    def test_invalid_import_some_modules_inline(self):
        source_code = 'import module1, module2, module3'
        self.assertBad(source_code, UnsupportedImportException)

    def test_invalid_import_some_names_from(self):
        source_code = 'from module1 import name1, name2'
        self.assertBad(source_code, UnsupportedImportException)

    def test_invalid_import_one_name_from(self):
        source_code = 'from module1 import name1'
        self.assertBad(source_code, UnsupportedImportException)

    def test_allowed_import(self):
        source_code = 'from module1 import *'
        result_code = '#include <module1.h>\n\n'
        self.assertSuccess(source_code, result_code)

    def test_allowed_multiline_import(self):
        source_code = 'from module1 import *\nfrom module2 import *'
        result_code = '#include <module1.h>\n#include <module2.h>\n\n'
        self.assertSuccess(source_code, result_code)

    def test_allowed_import_not_from_std(self):
        source_code = 'from .module1 import *'
        result_code = '#include "./module1.h"\n\n'
        self.assertSuccess(source_code, result_code)

    def test_allowed_import_not_from_std_parent_dir(self):
        source_code = 'from ..module1 import *'
        result_code = '#include "../module1.h"\n\n'
        self.assertSuccess(source_code, result_code)

    def test_allowed_import_not_from_std_more_parent_dirs(self):
        source_code = 'from ...module1 import *'
        result_code = '#include "../../module1.h"\n\n'
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

    def test_function_with_one_default_ars(self):
        source_code = (
            'def function(arg1: float, arg2: char, arg3: int = 10) -> int:\n'
            '    a: int = 5\n'
            '    return a + arg1'
        )
        result_code = (
            'int function(float arg1, char arg2, int arg3) {\n'
            '    int a = 5;\n'
            '    return a + arg1;\n'
            '}\n'
            'int function(float arg1, char arg2) {\n'
            '    return function(arg1, arg2, 10);\n'
            '}\n'
        )
        self.assertSuccess(source_code, result_code)

    def test_function_with_default_ars(self):
        source_code = (
            'def function(arg1: float, arg2: char, arg3: int = 10, arg4: int = 55) -> int:\n'
            '    a: int = 5\n'
            '    return a + arg1'
        )
        result_code = (
            'int function(float arg1, char arg2, int arg3, int arg4) {\n'
            '    int a = 5;\n'
            '    return a + arg1;\n'
            '}\n'
            'int function(float arg1, char arg2, int arg3) {\n'
            '    return function(arg1, arg2, arg3, 55);\n'
            '}\n'
            'int function(float arg1, char arg2) {\n'
            '    return function(arg1, arg2, 10, 55);\n'
            '}\n'
        )
        self.assertSuccess(source_code, result_code)

    def test_function_with_default_ars_no_return(self):
        source_code = (
            'def function(arg1: float, arg2: char, arg3: int = 10, arg4: int = 55):\n'
            '    a: int = 5\n'
            '    a = a + arg1'
        )
        result_code = (
            'void function(float arg1, char arg2, int arg3, int arg4) {\n'
            '    int a = 5;\n'
            '    a = a + arg1;\n'
            '}\n'
            'void function(float arg1, char arg2, int arg3) {\n'
            '    function(arg1, arg2, arg3, 55);\n'
            '}\n'
            'void function(float arg1, char arg2) {\n'
            '    function(arg1, arg2, 10, 55);\n'
            '}\n'
        )
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
    # TODO: так как одна инструкция. то не использовать фигурные скобки
    def test_if(self):
        source_code = 'if variable > 1:\n    variable2 = 2'
        result_code = 'if (variable > 1) {\n    variable2 = 2;\n}\n\n'
        self.assertSuccess(source_code, result_code)

    # TODO: так как одна инструкция. то не использовать фигурные скобки
    def test_if_else(self):
        source_code = 'if variable > 1:\n    variable2 = 2\nelse:\n    variable3 = 3'
        result_code = 'if (variable > 1) {\n    variable2 = 2;\n} else {\n    variable3 = 3;\n}\n\n'
        self.assertSuccess(source_code, result_code)

    # TODO: так как одна инструкция. то не использовать фигурные скобки
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

    def test_if_multiline(self):
        source_code = (
            'if variable1 == 1:\n'
            '    variable2 = 2\n'
            '    function1()\n'
        )
        result_code = (
            'if (variable1 == 1) {\n'
            '    variable2 = 2;\n'
            '    function1();\n'
            '}\n\n'
        )
        self.assertSuccess(source_code, result_code)

    def test_if_else_multiline(self):
        source_code = (
            'if variable > 1:\n'
            '    variable2 = 2\n'
            '    function1()\n'
            'else:\n'
            '    variable3 = 3\n'
            '    function2()\n'
        )
        result_code = (
            'if (variable > 1) {\n'
            '    variable2 = 2;\n'
            '    function1();\n'
            '} else {\n'
            '    variable3 = 3;\n'
            '    function2();\n'
            '}\n\n')
        self.assertSuccess(source_code, result_code)

    def test_if_elif_else_multiline(self):
        source_code = (
            'if var > 1:\n'
            '    var2 = 2\n'
            '    function1()\n'
            'elif var < -10:\n'
            '    var4 = 4\n'
            '    function2()\n'
            'elif var < -5:\n'
            '    var5 = 5\n'
            'else:\n'
            '    var3 = 3\n'
            '    function3()\n'
        )
        result_code = (
            'if (var > 1) {\n'
            '    var2 = 2;\n'
            '    function1();\n'
            '} else if (var < -10) {\n'
            '    var4 = 4;\n'
            '    function2();\n'
            '} else if (var < -5) {\n'
            '    var5 = 5;\n'
            '} else {\n'
            '    var3 = 3;\n'
            '    function3();\n'
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
    def test_function_oneline_docstring(self):
        source_code = (
            'def function():\n'
            '    """ test docstring"""\n'
        )
        result_code = (
            '\n/*\n'
            'test docstring\n'
            '*/\n'
            'void function(void) {\n}\n'
        )
        self.assertSuccess(source_code, result_code)

    def test_function_multiline_docstring(self):
        source_code = (
            'def function():\n'
            '    """\n'
            '    test docstring\n'
            '    the second test docstring\n'
            '    """\n'
        )
        result_code = (
            '\n/*\n'
            'test docstring\n'
            'the second test docstring\n'
            '*/\n'
            'void function(void) {\n}\n'
        )
        self.assertSuccess(source_code, result_code)

    def test_function_multiline_comment(self):
        source_code = (
            'some_var = 1\n'
            '"""\n'
            'test comment\n'
            'the second test comment\n'
            '"""\n'
        )
        result_code = (
            'some_var = 1;\n'
            '\n/*\n'
            'test comment\n'
            'the second test comment\n'
            '*/\n'
        )
        self.assertSuccess(source_code, result_code)


class PointerTestCase(Py2CTestCase):
    def test_pointer_using(self):
        source_code = 'function(variable.link)'
        result_code = 'function(&variable);\n'
        self.assertSuccess(source_code, result_code)

    def test_pointer_initing(self):
        source_code = 'variable: int__link'
        result_code = 'int *variable;\n'
        self.assertSuccess(source_code, result_code)


class ArraysTestCase(Py2CTestCase):
    def test_array_assign(self):
        source_code = 'variable[10] = 50'
        result_code = 'variable[10] = 50;\n'
        self.assertSuccess(source_code, result_code)

    def test_array_using(self):
        source_code = 'variable1 = variable2[variable3]'
        result_code = 'variable1 = variable2[variable3];\n'
        self.assertSuccess(source_code, result_code)

    def test_array_init_static_one_depth(self):
        """Данный тест является излишним, т. к. при указании значения C-компилятор сам вычислит длину массива"""
        source_code = 'variable: int__3 = [5, 10, 15]'
        result_code = 'int variable[3] = {5, 10, 15};\n'
        self.assertSuccess(source_code, result_code)

    def test_array_init_static_one_depth_autosize(self):
        source_code = 'variable: int = [5, 10, 15]'
        result_code = 'int variable[] = {5, 10, 15};\n'
        self.assertSuccess(source_code, result_code)

    def test_array_init_static_one_depth_pointer(self):
        source_code = 'variable: int__link = [5, 10, 15, 20]'
        result_code = 'int *variable[] = {5, 10, 15, 20};\n'
        self.assertSuccess(source_code, result_code)

    def test_array_init_static_one_depth_empty(self):
        source_code = 'variable: int__3'
        result_code = 'int variable[3];\n'
        self.assertSuccess(source_code, result_code)

    def test_array_init_static_multi_depth_empty(self):
        source_code = 'variable: int__3__4__1'
        result_code = 'int variable[3][4][1];\n'
        self.assertSuccess(source_code, result_code)


class BooleanTestCase(Py2CTestCase):
    def test_false(self):
        source_code = 'variable = False'
        result_code = 'variable = 0;\n'
        self.assertSuccess(source_code, result_code)

    def test_true(self):
        source_code = 'while True: pass'
        result_code = 'while (1) {\n}\n\n'
        self.assertSuccess(source_code, result_code)

    def test_bool_sequence(self):
        source_code = (
            'if y + 2 * x < a or x > 30 or y > 20:\n'
            '    k += 1'
        )
        result_code = (
            'if (y + (2 * x) < a || x > 30 || y > 20) {\n'
            '    k += 1;\n'
            '}\n\n'
        )
        self.assertSuccess(source_code, result_code)

    def test_bool_sequence_with_parent(self):
        source_code = (
            'if (y + 2 and x < a) or x > 30 or y > 20:\n'
            '    k += 1'
        )
        result_code = (
            'if ((y + 2 && x < a) || x > 30 || y > 20) {\n'
            '    k += 1;\n'
            '}\n\n'
        )
        self.assertSuccess(source_code, result_code)


class ForTestCase(Py2CTestCase):
    def test_for(self):
        source_code = 'for j in range(0, 5): pass'
        result_code = 'for (j=0; j<5; j++) {\n}\n\n'
        self.assertSuccess(source_code, result_code)


class ReturningSeveralValuesTestCase(Py2CTestCase):
    def test_several_values(self):
        source_code = (
            'def function() -> int:\n'
            '    value1: int = 5\n'
            '    value2: char = "k"\n'
            '    return value1, value2'
        )
        result_code = (
            'int function(void) {\n'
            '    int value1 = 5;\n'
            '    char value2 = "k";\n'
            '    struct function_mys _function_mys = {value1, value2};\n'
            '    return _function_mys;\n'
            '}\n'
        )
        self.assertSuccess(source_code, result_code)


class PowTestCase(Py2CTestCase):
    def test_pow(self):
        source_code = (
            'a: int = a ** b'
        )
        result_code = (
            '#include <cmath>\n\n'
            'int a = pow(a, b);\n'
        )
        self.assertSuccess(source_code, result_code)

    def test_pow_with_imports(self):
        source_code = (
            'from module1 import *\n'
            'a: int = 10\n'
            'b: int = 3\n'
            'c: int = a ** b'
        )
        result_code = (
            '#include <cmath>\n'
            '#include <module1.h>\n\n'
            'int a = 10;\n'
            'int b = 3;\n'
            'int c = pow(a, b);\n'
        )
        self.assertSuccess(source_code, result_code)


# class LambdaTestCase(Py2CTestCase):
#     def test_lambda(self):
#         # Выбрасывать исключение, так как у аргументов лямбды невозможно указать аннотацию
#         source_code = "variable1: int = lambda x, y: x + y"
#         self.assertBad(source_code, LambdaIsNotAllowedHereException)


if __name__ == '__main__':
    unittest.main()
