from sys import version_info
from typing import Optional, List, Tuple

from py2c.exceptions import NoneIsNotAllowedException, SourceCodeException, UnsupportedImportException


if version_info.minor > 6:
    from dataclasses import dataclass, field

    @dataclass
    class Annotation:
        type: str
        array_sizes: List[str] = field(default_factory=list)
        link: bool = False
else:
    class Annotation:
        type: str
        array_sizes = None
        link = False

        def __init__(self, **kwargs):
            for n, v in kwargs.items():
                setattr(self, n, v)


class TranslatorC:
    def __init__(self, save_to, config=None):
        self.config = {} if config is None else config
        self.save_to = save_to
        self.level = 0

        self.col_offset = None
        self.lineno = None
        self._walk = None
        self.transit_data = {}
        self.current_function_names = []

        self.raw_strings = []
        self.raw_imports = set()

    def write(self, data: str):
        # self.save_to.write(data)
        self.raw_strings.append(data)

    def write_lbracket(self, is_need_brackets):
        if is_need_brackets:
            self.write('(')

    def write_rbracket(self, is_need_brackets):
        if is_need_brackets:
            self.write(')')

    def save(self):
        raw_imports = list(self.raw_imports)
        raw_imports.sort()
        str_imports = '\n'.join(raw_imports)
        if str_imports:
            self.save_to.write(str_imports)
            self.save_to.write('\n\n')

        self.save_to.write(''.join(self.raw_strings))

    @property
    def ident(self):
        return '    ' * self.level

    @property
    def parent_node(self):
        return self.transit_data['parents'][-1]

    @property
    def current_function_name(self):
        return self.current_function_names[-1]

    def walk(self, node, level: int = 0, current_function_name: str = None):
        if current_function_name:
            self.current_function_names.append(current_function_name)

        self.level += level
        self._walk(self, node)
        self.level -= level
        if current_function_name:
            self.current_function_names.pop()

    def parse_annotation(self, annotation: str):
        params = {'array_sizes': []}
        parts = annotation.split('__')
        while parts and parts[-1].isdigit():  # TODO:   убедиться, что метод возвращает Истину лишь для арабских цифр
            params['array_sizes'].append(parts.pop())

        if parts and parts[-1] == 'auto':
            parts.pop()
            params['array_sizes'].append('')

        if parts and parts[-1] == 'link':
            parts.pop()
            params['link'] = True

        #if parts and parts[-1] in ('int', 'char'):  # TODO: Перечислить нормальные типы и вынести их в константу
        if parts:
            params['type'] = ' '.join(parts)
        else:
            raise SourceCodeException('Annotation should have type', self.parent_node)

        # if 'static' in parts:
        # if 'const' in parts:
        # if 'eeprom' in parts:

        return Annotation(**params)

    def process_init_variable(self, name, value_expr, annotation: Optional[str], value_lambda=None):
        annotation = self.parse_annotation(annotation)
        if annotation.type == 'preproc':
            self.write(f'#define ')
            self.walk(name)
            if value_expr:
                self.write(' ')
                self.walk(value_expr)
            elif value_lambda:
                args, body = value_lambda
                self.write('({}) '.format(','.join(args)))
                self.walk(body)
            else:
                raise SourceCodeException('The constant must have a value', self.parent_node)

            self.write('\n')
        else:
            self.write(f'{self.ident}{annotation.type} ')
            if annotation.link:
                self.write('*')

            self.write(name) if isinstance(name, str) else self.walk(name)
            for array_size in annotation.array_sizes:
                self.write(f'[{array_size}]')

            if value_expr:
                self.write(' = ')
                self.walk(value_expr)

            self.write(';\n')

    def process_assign_variable(self, names, value):
        self.write(self.ident)
        for name in names:
            self.walk(name)
            self.write(' = ')

        self.walk(value)
        self.write(';\n')

    def process_augassign_variable(self, name, value, operator):
        self.write(self.ident)
        self.walk(name)
        self.write(f' {operator}= ')
        self.walk(value)
        self.write(';\n')

    def process_multiline_comment(self, comment):
        self.write(f'\n{self.ident}/*\n')
        for line in comment.strip().split('\n'):
            self.write(f'{self.ident}{line}\n')

        self.write(f'{self.ident}*/\n')

    def process_oneline_comment(self, comment):
        self.write(f'{self.ident}// {comment}\n')

    def process_def_function(
            self,
            name: str,
            annotation: Optional[str],
            pos_args: Tuple[str],
            pos_args_defaults,
            body,
            docstring_comment: str
    ):
        if annotation is None:
            annotation = 'void'

        if docstring_comment:
            self.process_multiline_comment(docstring_comment)

        self.write(f'{self.ident}{annotation} {name}(')
        str_args = [f'{annotation_arg} {name_arg}' for annotation_arg, name_arg in pos_args]
        self.write(', '.join(str_args) if pos_args else 'void')
        self.write(') {\n')
        for expression in body:
            self.walk(expression, 1, current_function_name=name)

        self.write('}\n')

        return_expr = '' if annotation == 'void' else 'return '

        for index_default_arg in range(1, len(pos_args_defaults)+1):
            self.write(f'{self.ident}{annotation} {name}(')
            str_args = [f'{annotation_arg} {name_arg}' for annotation_arg, name_arg in pos_args[:-index_default_arg]]
            self.write(', '.join(str_args) if pos_args else 'void')
            self.write(') {\n')
            self.level += 1
            self.write(f'{self.ident}{return_expr}{name}(')
            self.level -= 1
            for annotation_arg, name_arg in pos_args[:-index_default_arg]:
                self.write(f'{name_arg}, ')

            for index_pos_arg_default, pos_arg_default in enumerate(pos_args_defaults[-index_default_arg:]):
                pos_arg_default.custom_ignore = False
                self.walk(pos_arg_default)
                if index_pos_arg_default < len(pos_args_defaults[-index_default_arg:]) - 1:
                    self.write(', ')

            self.write(');\n')
            self.write('}\n')

    def process_call_function(self, name, pos_args):
        self.walk(name)
        self.write('(')
        for pos_arg_index, pos_arg in enumerate(pos_args, 1):
            self.walk(pos_arg)
            if pos_arg_index < len(pos_args):
                self.write(', ')

        self.write(')')

    def process_constant(self, value, parent_node):
        if value is None:
            raise NoneIsNotAllowedException('None is forbidden', parent_node)

        elif isinstance(value, str):
            self.write(f'"{value}"')
        elif isinstance(value, bool):
            self.write('{}'.format(1 if value else 0))
        elif isinstance(value, (int, float)):
            self.write(f'{value}')

    def process_name(self, name):
        self.write(name)

    def process_delete_variable(self, names):
        for name in names:
            self.write('delete ')
            self.walk(name)
            self.write(';\n')

    def process_continue(self):
        self.write(f'{self.ident}continue;\n')

    def process_binary_op(self, operand_left, operator, operand_right, is_need_brackets):
        self.write_lbracket(is_need_brackets)
        self.walk(operand_left)
        self.write(f' {operator} ')
        self.walk(operand_right)
        self.write_rbracket(is_need_brackets)

    def process_binary_op_pow(self, operand_left, operand_right, is_need_brackets):
        module_name = 'cmath'
        self.raw_imports.add(f'#include <{module_name}>')
        self.write_lbracket(is_need_brackets)
        self.write(f'pow(')
        self.walk(operand_left)
        self.write(f', ')
        self.walk(operand_right)
        self.write(f')')
        self.write_rbracket(is_need_brackets)
        # if not is_need_brackets:
        #     self.write(f';')

    def process_unary_op(self, operand, operator):
        self.write(f'{operator}')
        self.walk(operand)

    def process_return(self, expression):
        self.write(f'{self.ident}return')
        if expression:
            self.write(' ')
            self.walk(expression)

        self.write(';\n')

    def process_multi_return(self, expressions):
        # TODO: Добавить аргументов к струткуре
        # TODO: Объявление структуры
        # TODO: Изменить аннотацию типа функции (struct function_mys)
        structure_name = f'{self.current_function_name}_mys'
        variable_name = f'_{structure_name}'
        self.process_init_variable(name=variable_name, value_expr=expressions, annotation=f'struct__{structure_name}')
        self.write(f'{self.ident}return {variable_name};\n')

    def process_while(self, condition, body, orelse):
        if orelse:
            self.write(f'{self.ident}unsigned byte success = 1;\n')

        self.write(f'{self.ident}while (')
        self.walk(condition)
        self.write(') {\n')
        for expression in body:
            self.walk(expression, 1)

        self.write(f'{self.ident}}}\n\n')

        if orelse:
            self.write(f'{self.ident}if (success == 1) {{\n')
            for expression in orelse:
                self.walk(expression, 1)

            self.write(f'{self.ident}}}\n\n')

    def process_import_from(self, module_name, imported_objects: List[Tuple[str]], level: int):
        if len(imported_objects) > 1 or imported_objects[0][0] != '*':
            raise UnsupportedImportException(
                'This import is not supported. Use `from module_name import *`',
                self.parent_node,
            )

        module_name = module_name.replace('.', '/')
        if level == 0:
            self.raw_imports.add(f'#include <{module_name}.h>')
        else:
            parent_path = './' if level == 1 else '../'*(level-1)
            self.raw_imports.add(f'#include "{parent_path}{module_name}.h"')

    def process_import(self, module_names):
        raise UnsupportedImportException(
            'This import is not supported. Use `from module_name import *`',
            self.parent_node,
        )
        # for module_name in module_names:
        #     module_name = module_name.replace('.', '/')
        #     self.write(f'#include <{module_name}.h>\n')
        #
        # self.write('\n')

    def process_expression(self, expression):
        self.write(self.ident)
        self.walk(expression)
        self.write(';\n')

    def process_if(self, condition, body, ifelses, orelse):
        self.write(f'{self.ident}if (')
        self.walk(condition)
        self.write(') {\n')
        for expression in body:
            self.walk(expression, 1)

        self.write(f'{self.ident}}}')

        for ifelse_condition, ifelse_body in ifelses:
            self.write(' else if (')
            self.walk(ifelse_condition)
            self.write(') {\n')
            for expression in ifelse_body:
                self.walk(expression, 1)

            self.write(f'{self.ident}}}')

        if orelse:
            self.write(' else ')
            self.write('{\n')
            for expression in orelse:
                self.walk(expression, 1)

            self.write(f'{self.ident}}}')

        self.write('\n\n')

    def process_compare(self, operand_left, operators, operands_right):
        self.walk(operand_left)
        for operator, operand_right in zip(operators, operands_right):
            self.write(f' {operator} ')
            self.walk(operand_right)

    def process_bool_op(self, operand_left, operator, operands_right, is_need_brackets):
        self.write_lbracket(is_need_brackets)
        self.walk(operand_left)
        for operand_right in operands_right:
            self.write(f' {operator} ')
            self.walk(operand_right)

        self.write_rbracket(is_need_brackets)

    def process_break(self, has_while_orelse):
        if has_while_orelse:
            self.write(f'{self.ident}success = 0;\n')

        self.write(f'{self.ident}break;\n')

    def process_ifexpr(self, condition, body, orelse, is_need_brackets):
        # #process_assign_variable
        # self.write(f'{self.ident}if (')
        # self.walk(condition)
        # self.write(') {\n')
        # self.walk(body, 1)
        # # self.write(';\n')
        # self.write(f'{self.ident}}} else {{\n')
        # self.walk(orelse, 1)
        # # converter.write(';\n')
        # self.write(f'{self.ident}}}\n\n')

        self.write_lbracket(is_need_brackets)
        self.write('(')
        self.walk(condition)
        self.write(') ? ')
        self.walk(body)
        self.write(' : ')
        self.walk(orelse)
        self.write_rbracket(is_need_brackets)

    def process_link(self, value):
        self.write('&')
        self.walk(value)

    def process_lambda(self, args, body):  # only for #define. TODO: build functions for another cases
        self.write('({}) '.format(','.join(args)))
        self.walk(body)

    def process_subscript(self, variable, index):
        self.walk(variable)
        self.write('[')
        self.walk(index)
        self.write(']')

    def process_array(self, elements):
        self.write('{')
        for index, element in enumerate(elements, 1):
            self.walk(element)
            if index < len(elements):
                self.write(', ')

        self.write('}')

    def process_for_function(self, name, body, function_name, args):
        self.write(f'{self.ident}for ({name}=')
        if len(args) >= 2:
            self.walk(args[0])
        else:
            self.write('0')

        self.write(f'; {name}<')

        if len(args) == 1:
            self.walk(args[0])
        elif len(args) >= 2:
            self.walk(args[1])
        else:
            raise Exception('Unsupported count of arguments for `range`')

        self.write(f'; {name}++) {{\n')
        for expression in body:
            self.walk(expression, 1)

        self.write(f'{self.ident}}}\n\n')