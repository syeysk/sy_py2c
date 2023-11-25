import pytest
from pytest import raises

from py2c.exceptions import (
    InvalidAnnotationException,
    NoneIsNotAllowedException,
)
from py2c.shortcuts import trans_c as trans


class TestOperatorsAndVariables:
    def test_init_variables_with_valid_annotation(self):
        source_code = 'variable1: \'int\' = 1\nvariable2: int = 1'
        result_code = 'int variable1 = 1;\nint variable2 = 1;\n'
        assert trans(source_code) == result_code

    def test_init_variables_with_invalid_annotation_1(self):
        with raises(InvalidAnnotationException):
            trans('a: a + b = 1')

    def test_init_variables_with_invalid_annotation_2(self):
        with raises(InvalidAnnotationException):
            trans('b: print(1) = 1')

    def test_init_empty_variables(self):
        source_code = 'variable1: int'
        result_code = 'int variable1;\n'
        assert trans(source_code) == result_code

    def test_init_string_variable(self):
        source_code = 'variable: char = \'1\''
        result_code = 'char variable = \"1\";\n'
        assert trans(source_code) == result_code

    def test_init_string_variable2(self):
        source_code = 'variable: char = \'a\''
        result_code = 'char variable = \"a\";\n'
        assert trans(source_code) == result_code

    def test_init_some_variables_with_the_different_types(self):
        source_code = 'a: int\nb: float\nc: char'
        result_code = 'int a;\nfloat b;\nchar c;\n'
        assert trans(source_code) == result_code

    # def test_init_some_variables_with_the_same_types(self):
    #     source_code = 'a: int\nb: int\nc: int'
    #     result_code = 'int a, b, c;\n'
    #     assert trans(source_code) == result_code

    def test_init_variable_without_type(self):
        source_code = (
            'variable = 10\n'
            'variable2 = -10\n'
            'variable3 = 10.5\n'
            'variable4 = -10.5\n'
            'variable5 = True\n'
            'variable6 = "i am a string"'
        )
        result_code = (
            'int variable = 10;\n'
            'signed int variable2 = -10;\n'
            'float variable3 = 10.5;\n'
            'signed float variable4 = -10.5;\n'
            'bool variable5 = 1;\n'
            'string variable6 = "i am a string";\n'
        )
        assert trans(source_code) == result_code


class TestNone:
    def test_none_value_of_variable(self):
        with raises(NoneIsNotAllowedException):
            trans('variable2: int = None')

    def test_none_annotation_of_variable(self):
        with raises(NoneIsNotAllowedException):
            trans('variable2: None = 1')

    def test_none_annotation_of_function(self):
        with raises(NoneIsNotAllowedException):
            trans('def function() -> None:\n    pass')

    def test_typed_function_with_return_none(self):
        with raises(NoneIsNotAllowedException):
            trans('def function(): return None')


class TestUnaryOperators:
    def test_usub(self):
        source_code = 'variable: int = 1\nvariable = -variable'
        result_code = 'int variable = 1;\nvariable = -variable;\n'
        assert trans(source_code) == result_code

    def test_uadd(self):
        source_code = 'variable: int = 1\nvariable = +variable'
        result_code = 'int variable = 1;\nvariable = +variable;\n'
        assert trans(source_code) == result_code

    def test_not(self):
        source_code = 'variable: int = 1\nvariable = not variable'
        result_code = 'int variable = 1;\nvariable = !variable;\n'
        assert trans(source_code) == result_code

    def test_invert(self):
        source_code = 'variable: int = 1\nvariable = ~variable'
        result_code = 'int variable = 1;\nvariable = ~variable;\n'
        assert trans(source_code) == result_code


class TestTernaryOperator:
    def test_ternary(self):
        source_code = 'a: int = 1\nb: int\nb = 10 if a == 99 else b'
        result_code = 'int a = 1;\nint b;\nb = (a == 99) ? 10 : b;\n'
        assert trans(source_code) == result_code


class TestDelete:
    def test_delete(self):
        source_code = 'del a, b'
        result_code = 'delete a;\ndelete b;\n'
        assert trans(source_code) == result_code


class TestPreprocConstants:
    def test_variable_preproc(self):
        source_code = 'TEST_CONST: preproc = 56'
        result_code = '#define TEST_CONST 56\n'
        assert trans(source_code) == result_code

    def test_function(self):
        source_code = 'TEST_FUNC: preproc = lambda x, y: x-y*7'
        result_code = '#define TEST_FUNC(x,y) x - (y * 7)\n'
        assert trans(source_code) == result_code


class TestImport:
    def test_invalid_import_one_module(self):
        source_code = 'import module1'
        result_code = '#include "module1.h"\n\n'
        assert trans(source_code) == result_code

    def test_invalid_import_one_module2(self):
        source_code = 'import module1 as m1'
        result_code = '#include "module1.h"\n\n'
        assert trans(source_code) == result_code

    def test_invalid_import_some_modules_inline(self):
        source_code = 'import module1, module2, module3'
        result_code = (
            '#include "module1.h"\n'
            '#include "module2.h"\n'
            '#include "module3.h"\n\n'
        )
        assert trans(source_code) == result_code

    def test_invalid_import_some_names_from(self):
        source_code = 'from module1 import name1, name2'
        result_code = '#include "module1.h"\n\n'
        assert trans(source_code) == result_code

    def test_invalid_import_one_name_from(self):
        source_code = 'from module1 import name1'
        result_code = '#include "module1.h"\n\n'
        assert trans(source_code) == result_code

    def test_allowed_import(self):
        source_code = 'from module1 import *'
        result_code = '#include "module1.h"\n\n'
        assert trans(source_code) == result_code

    def test_allowed_multiline_import(self):
        source_code = 'from module1 import *\nfrom module2 import *'
        result_code = '#include "module1.h"\n#include "module2.h"\n\n'
        assert trans(source_code) == result_code

    def test_allowed_import_not_from_std(self):
        source_code = 'from .module1 import *'
        result_code = '#include "module1.h"\n\n'
        assert trans(source_code) == result_code

    def test_allowed_import_not_from_std_parent_dir(self):
        source_code = 'from ..module1 import *'
        result_code = '#include "../module1.h"\n\n'
        assert trans(source_code) == result_code

    def test_allowed_import_not_from_std_more_parent_dirs(self):
        source_code = 'from ...module1 import *'
        result_code = '#include "../../module1.h"\n\n'
        assert trans(source_code) == result_code


class TestFunction:
    def test_empty_function(self):
        source_code = 'def function(): pass'
        result_code = 'void function(void) {\n}\n'
        assert trans(source_code) == result_code

    def test_empty_typed_function(self):
        source_code = 'def function() -> int: pass'
        result_code = 'int function(void) {\n}\n'
        assert trans(source_code) == result_code

    def test_typed_function_with_return(self):
        source_code = 'def function() -> int: return 34'
        result_code = 'int function(void) {\n    return 34;\n}\n'
        assert trans(source_code) == result_code

    def test_typed_function_with_return_and_args(self):
        source_code = 'def function(arg1: float, arg2: char) -> int:\n    a: int = 5\n    return a + arg1'
        result_code = 'int function(float arg1, char arg2) {\n    int a = 5;\n    return a + arg1;\n}\n'
        assert trans(source_code) == result_code

    def test_typed_function_with_return_none(self):
        source_code = 'def function(): return'
        result_code = 'void function(void) {\n    return;\n}\n'
        assert trans(source_code) == result_code

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
        assert trans(source_code) == result_code

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
        assert trans(source_code) == result_code

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
        assert trans(source_code) == result_code

    def test_calling_function(self):
        source_code = 'function(arg1, 1)'
        result_code = 'function(arg1, 1);\n'
        assert trans(source_code) == result_code

    def test_assign_calling_function(self):
        source_code = 'variable: int = function(arg1, 1)'
        result_code = 'int variable = function(arg1, 1);\n'
        assert trans(source_code) == result_code

    def test_assign_calling_function_with_ternary_op(self):
        source_code = 'variable: int = function(arg1, 5 if c > 45 else d)'
        result_code = 'int variable = function(arg1, ((c > 45) ? 5 : d));\n'
        assert trans(source_code) == result_code


class TestIf:
    # TODO: так как одна инструкция. то не использовать фигурные скобки
    def test_if(self):
        source_code = (
            'variable2: int\n'
            'if variable > 1:\n'
            '    variable2 = 2'
        )
        result_code = (
            'int variable2;\n'
            'if (variable > 1) {\n'
            '    variable2 = 2;\n'
            '}\n\n'
        )
        assert trans(source_code) == result_code

    # TODO: так как одна инструкция. то не использовать фигурные скобки
    def test_if_else(self):
        source_code = (
            'variable2: int\n'
            'variable3: int\n'
            'if variable > 1:\n'
            '    variable2 = 2\n'
            'else:\n'
            '    variable3 = 3'
        )
        result_code = (
            'int variable2;\n'
            'int variable3;\n'
            'if (variable > 1) {\n'
            '    variable2 = 2;\n'
            '} else {\n'
            '    variable3 = 3;\n'
            '}\n\n'
        )
        assert trans(source_code) == result_code

    # TODO: так как одна инструкция. то не использовать фигурные скобки
    def test_if_elif_else(self):
        source_code = (
            'var2: int\n'
            'var3: int\n'
            'var4: int\n'
            'var5: int\n'
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
            'int var2;\n'
            'int var3;\n'
            'int var4;\n'
            'int var5;\n'
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
        assert trans(source_code) == result_code

    def test_if_multiline(self):
        source_code = (
            'variable2: int\n'
            'if variable1 == 1:\n'
            '    variable2 = 2\n'
            '    function1()\n'
        )
        result_code = (
            'int variable2;\n'
            'if (variable1 == 1) {\n'
            '    variable2 = 2;\n'
            '    function1();\n'
            '}\n\n'
        )
        assert trans(source_code) == result_code

    def test_if_else_multiline(self):
        source_code = (
            'variable2: int\n'
            'variable3: int\n'
            'if variable > 1:\n'
            '    variable2 = 2\n'
            '    function1()\n'
            'else:\n'
            '    variable3 = 3\n'
            '    function2()\n'
        )
        result_code = (
            'int variable2;\n'
            'int variable3;\n'
            'if (variable > 1) {\n'
            '    variable2 = 2;\n'
            '    function1();\n'
            '} else {\n'
            '    variable3 = 3;\n'
            '    function2();\n'
            '}\n\n'
        )
        assert trans(source_code) == result_code

    def test_if_elif_else_multiline(self):
        source_code = (
            'var2: int\n'
            'var3: int\n'
            'var4: int\n'
            'var5: int\n'
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
            'int var2;\n'
            'int var3;\n'
            'int var4;\n'
            'int var5;\n'
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
        assert trans(source_code) == result_code


class TestWhile:
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
        assert trans(source_code) == result_code

    def test_while_else(self):
        source_code = (
            'variable: int\n'
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
            'int variable;\n'
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
        assert trans(source_code) == result_code


class TestComment:
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
        assert trans(source_code) == result_code

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
        assert trans(source_code) == result_code

    def test_function_multiline_comment(self):
        source_code = (
            'some_var: int = 1\n'
            '"""\n'
            'test comment\n'
            'the second test comment\n'
            '"""\n'
        )
        result_code = (
            'int some_var = 1;\n'
            '\n/*\n'
            'test comment\n'
            'the second test comment\n'
            '*/\n'
        )
        assert trans(source_code) == result_code


class TestPointer:
    def test_pointer_using(self):
        source_code = 'function(variable.link)'
        result_code = 'function(&variable);\n'
        assert trans(source_code) == result_code

    def test_pointer_initing(self):
        source_code = 'variable: int__link'
        result_code = 'int *variable;\n'
        assert trans(source_code) == result_code


class TestStaticArrays:
    def test_array_assign(self):
        source_code = 'variable[10] = 50'
        result_code = 'variable[10] = 50;\n'
        assert trans(source_code) == result_code

    def test_array_using(self):
        source_code = 'variable1 = variable2[variable3]'
        result_code = 'variable1 = variable2[variable3];\n'
        assert trans(source_code) == result_code

    def test_array_init_static_one_depth(self):
        """Данный тест является излишним, т. к. при указании значения C-компилятор сам вычислит длину массива"""
        source_code = 'variable: int__3 = [5, 10, 15]'
        result_code = 'int variable[3] = {5, 10, 15};\n'
        assert trans(source_code) == result_code

    def test_array_init_static_one_depth_string(self):
        source_code = 'variable: char__32 = \'example string\''
        result_code = 'char variable[32] = "example string";\n'
        assert trans(source_code) == result_code

    def test_array_init_static_one_depth_autosize(self):
        source_code = 'variable: int = [5, 10, 15]'
        result_code = 'int variable[] = {5, 10, 15};\n'
        assert trans(source_code) == result_code

    def test_array_init_static_one_depth_pointer(self):
        source_code = 'variable: int__link = [5, 10, 15, 20]'
        result_code = 'int *variable[] = {5, 10, 15, 20};\n'
        assert trans(source_code) == result_code

    def test_array_init_static_one_depth_empty(self):
        source_code = 'variable: int__3'
        result_code = 'int variable[3];\n'
        assert trans(source_code) == result_code

    def test_array_init_static_one_depth_empty2(self):
        source_code = 'variable: int = []'
        result_code = 'int variable[] = {};\n'
        assert trans(source_code) == result_code

    def test_array_init_static_multi_depth_empty(self):
        source_code = 'variable: int__3__4__1'
        result_code = 'int variable[3][4][1];\n'
        assert trans(source_code) == result_code


# class TestDynamicArrays:
#     def test_array_init_dynamic_one_depth_empty(self):
#         source_code = (
#             'variable: int = []\n'
#             'variable.append(255)'
#         )
#         result_code = (
#             'int variable[] = {};\n'
#             'malloc();'
#             'variable.append(255);\n'
#         )
#         assert trans(source_code) == result_code


class TestAttributeAndMethods:
    def test_assign_attribute(self):
        source_code = 'variable: int = any_name.my_attribute'
        result_code = 'int variable = any_name.my_attribute;\n'
        assert trans(source_code) == result_code

    def test_assign_to_attribute(self):
        source_code = 'any_name.my_attribute = 56'
        result_code = 'any_name.my_attribute = 56;\n'
        assert trans(source_code) == result_code

    def test_call_method(self):
        source_code = 'EEPROM.put(address, value)'
        result_code = 'EEPROM.put(address, value);\n'
        assert trans(source_code) == result_code

    def test_subscript(self):
        source_code = 'value: int = array_struct[4].struct_field'
        result_code = 'int value = array_struct[4].struct_field;\n'
        assert trans(source_code) == result_code

    def test_subscript_like_expression(self):
        source_code = 'value: int = array_struct[i+5].struct_field'
        result_code = 'int value = array_struct[i + 5].struct_field;\n'
        assert trans(source_code) == result_code


class TestBoolean:
    def test_false(self):
        source_code = 'variable: bool = False'
        result_code = 'bool variable = 0;\n'
        assert trans(source_code) == result_code

    def test_true(self):
        source_code = 'while True: pass'
        result_code = 'while (1) {\n}\n\n'
        assert trans(source_code) == result_code

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
        assert trans(source_code) == result_code

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
        assert trans(source_code) == result_code


class TestFor:
    def test_for(self):
        source_code = 'for j in range(0, 5): pass'
        result_code = 'for (j=0; j<5; j++) {\n}\n\n'
        assert trans(source_code) == result_code


class TestReturningSeveralValues:
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
        assert trans(source_code) == result_code


class TestPow:
    def test_pow(self):
        source_code = (
            'a: int = a ** b'
        )
        result_code = (
            '#include "math.h"\n\n'
            'int a = pow(a, b);\n'
        )
        assert trans(source_code) == result_code

    def test_pow_with_imports(self):
        source_code = (
            'from module1 import *\n'
            'a: int = 10\n'
            'b: int = 3\n'
            'c: int = a ** b'
        )
        result_code = (
            '#include "math.h"\n'
            '#include "module1.h"\n\n'
            'int a = 10;\n'
            'int b = 3;\n'
            'int c = pow(a, b);\n'
        )
        assert trans(source_code) == result_code

    def test_pow_with_import_math(self):
        source_code = (
            'from math import sqrt\n'
            'a: int = sqrt(a ** b)'
        )
        result_code = (
            '#include "math.h"\n\n'
            'int a = sqrt(pow(a, b));\n'
        )
        assert trans(source_code) == result_code


@pytest.mark.parametrize(
    'method_name',
    (
        'floor ceil trunc fabs'  # Округление
        'sqrt cbrt exp log log10'  # Корни, степени, логарифмы
        'sin cos tan asin acos atan'  # Тригонометрия
    ).split(),
)
def test_math_methods(method_name):
    """
    math в c/c++: https://ejudge.179.ru/tasks/cpp/total/132.html
                  https://ru.wikipedia.org/wiki/Math.h
    math в python: https://docs.python.org/3/library/math.html
    """
    # TODO: round - встроенная функция в python
    # TODO: pow - принимает 2 аргумента
    # TODO: log - принимает второй необязательный аргумент в python
    source_code = (
        'from math import *\n'
        f'v: int = math.{method_name}(56)'
    )
    result_code = (
        '#include "math.h"\n\n'
        f'int v = {method_name}(56);\n'
    )
    assert trans(source_code) == result_code

# def test_math_constants(self):
#     const_names = {
#         'pi': 'M_PI'
#     }
#     for const_name, const_name_c in const_names.items():
#         self.setUp()
#         with self.subTest(msg=const_name):
#             source_code = (
#                 'from math import *\n'
#                 f'v: int = math.{const_name}'
#             )
#             result_code = (
#                 '#include <math.h>\n\n'
#                 f'int v = {const_name_c};\n'
#             )
#             self.assertSuccess(source_code, result_code)


# class TestLambda:
#     def test_lambda(self):
#         # Выбрасывать исключение, так как у аргументов лямбды невозможно указать аннотацию
#         source_code = "variable1: int = lambda x, y: x + y"
#         self.assertBad(source_code, LambdaIsNotAllowedHereException)


class TestPrint:
    def test_print_empty(self):
        source_code = (
            'print()'
        )
        result_code = (
            '#include "stdio.h"\n\n'
            'printf("\\n");'
            '\n'
        )
        assert trans(source_code) == result_code

    def test_print_one_string_arg(self):
        source_code = (
            'print(\'Hello world\')'
        )
        result_code = (
            '#include "stdio.h"\n\n'
            'printf("Hello world\\n");'
            '\n'
        )
        assert trans(source_code) == result_code
