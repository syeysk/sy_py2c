from dataclasses import dataclass, field

from py2c.exceptions import NoneIsNotAllowedException, SourceCodeException


@dataclass
class Annotation:
    type: str
    array_sizes: list[str] = field(default_factory=list)
    link: bool = False


class RawString:
    """Class to represent a string, which is changing during the translation"""

    def __init__(
        self,
        translater,
        level: int,
        ident: str,
    ):
        self.translater = translater
        self.level = level
        self.ident = ident
        self.prev_raw_string = None

    def set_previous_raw_string(self, prev_raw_string):
        self.prev_raw_string = prev_raw_string


class DeclarationVariableString(RawString):
    """Класс управления параметрами объявления переменной"""
    def __init__(self, annotation: Annotation, name: str, *args):
        super().__init__(*args)
        self.annotation = annotation
        self.name = name
        self.translater.set_variable_data(name, type=annotation.type)

    @property
    def variable_data(self):
        return self.translater.get_variable_data(self.name, self.level)

    def __str__(self):
        variable_type = self.variable_data.get('variable_type')
        if variable_type == 'dynamic_array':
            return (
                '{ident}int py2c_length_{name} = {array_size};\n'
                '{ident}{annotation} *{name}\n'
                '{ident}{name} = ({annotation} *)malloc(py2c_length_{name} * sizeof({annotation}));\n'
            ).format(annotation=self.annotation.type, name=self.name, array_size=self.array_size, ident=self.ident)

        link = '*' if self.annotation.link else ''
        array_sizes = self.annotation.array_sizes or self.variable_data.get('array_sizes', [])
        str_array_sizes = ''.join([f'[{array_size}]' for array_size in array_sizes])
        # if self.prev_raw_string and isinstance(self.prev_raw_string, DeclarationVariableString):
        #     if self.prev_raw_string.annotation.type == self.annotation.type:
        #         return f', {link}{self.name}{str_array_sizes}'

        return f'{self.ident}{self.annotation.type} {link}{self.name}{str_array_sizes}'


class TranslatorC:
    """
    > Если подключаемый файл указан в <>, то поиск будет происходить в стандартных каталогах,
      предназначенных для хранения заголовочных файлов.
      В случае, если подключаемый файл заключен в двойные кавычки, поиск будет происходить в текущем рабочем каталоге.
      Если файл не найден, то поиск продолжается в стандартных каталогах
    Источник: http://www.c-cpp.ru/books/include
    Подробнее: https://www.opennet.ru/docs/RUS/cpp/cpp-4.html

    Поэтому в большинстве случаев импорт модуля будет транслироваться в импорт пользовательского модуля, чтобы поведение
    препроцессора C было схожим с интерпретатором Python
    """
    STR_INCLUDE_USER_MODULE = '#include "{parent_path}{module_name}.h"'
    STR_INCLUDE_STD_MODULE = '#include <{module_name}.h>'
    STR_INCLUDE_MODULE_MATH = STR_INCLUDE_USER_MODULE.format(parent_path='', module_name='math')
    STR_INCLUDE_MODULE_STDIO = STR_INCLUDE_USER_MODULE.format(parent_path='', module_name='stdio')

    def __init__(self, save_to, config=None):
        self.config = {} if config is None else config
        self.save_to = save_to
        self.level = 0

        self.col_offset = None
        self.lineno = None
        self._walk = None
        self.transit_data = {}
        self.current_function_names = []
        self.variables_data = {}

        self.raw_strings = []
        self.raw_imports = set()

    def get_variable_data(self, name: str, level: int = None):
        level = self.level if level is None else level
        while level >= 0:
            variable_data = self.variables_data.get(level, {}).get(name)
            if variable_data:
                return variable_data

            level -= 1

        variable_data = {}
        self.variables_data[level] = {name: variable_data}
        return variable_data

    def set_variable_data(self, name: str, level: int = None, **kwargs):
        level = self.level if level is None else level
        self.variables_data.setdefault(level, {}).setdefault(name, {}).update(kwargs)

    def write(self, data: str | RawString):
        self.raw_strings.append(data)

    def write_lbracket(self, is_need_brackets):
        if is_need_brackets:
            self.write('(')

    def write_rbracket(self, is_need_brackets):
        if is_need_brackets:
            self.write(')')

    def save(self):
        if self.raw_imports:
            raw_imports = list(self.raw_imports)
            raw_imports.sort()
            str_imports = '\n'.join(raw_imports)
            self.save_to.write(str_imports)
            self.save_to.write('\n\n')

        prev_raw_string = None
        for raw_index, raw_string in enumerate(self.raw_strings):
            if isinstance(raw_string, RawString):
                raw_string.set_previous_raw_string(prev_raw_string)
                self.save_to.write(str(raw_string))
            else:
                # # replace '}\n\n}' by '}\n}' . в таком виде код работает вне контеста и может повлиять, например, на произвольные строки
                # if len(self.raw_strings) > raw_index+1:
                #     next_string = self.raw_strings[raw_index + 1]
                #     if isinstance(next_string, str) and next_string.strip() == '}' and raw_string.strip() in ('}', ''):
                #         raw_string = raw_string[:-1]

                self.save_to.write(raw_string)

            prev_raw_string = raw_string

        self.variables_data.clear()
        self.raw_strings.clear()
        self.raw_imports.clear()

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

        params['array_sizes'].reverse()

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

    def process_init_variable(self, name: str, value_expr, annotation: str | None, value_lambda=None):
        annotation = self.parse_annotation(annotation)
        if annotation.type == 'preproc':
            self.write(f'#define ')
            self.write(name)
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
            raw_string = DeclarationVariableString(annotation, name, self, self.level, self.ident)
            self.write(raw_string)
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

    def process_augassign_variable(self, name, value, operator: str):
        self.write(self.ident)
        self.walk(name)
        self.write(f' {operator}= ')
        self.walk(value)
        self.write(';\n')

    def process_multiline_comment(self, comment: str):
        self.write(f'\n{self.ident}/*\n')
        for line in comment.strip().split('\n'):
            self.write(f'{self.ident}{line}\n')

        self.write(f'{self.ident}*/\n')

    def process_oneline_comment(self, comment: str):
        self.write(f'{self.ident}// {comment}\n')

    def process_def_function(
            self,
            name: str,
            annotation: str | None,
            pos_args: tuple[str],
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

        if self.raw_strings[-1] == 'print':
            self.raw_imports.add(self.STR_INCLUDE_MODULE_STDIO)
            self.raw_strings[-1] = 'printf'

            if not pos_args:
                self.write('("\\n")')
            elif len(pos_args) == 1:
                self.write('(')
                self.walk(pos_args[0])
                last_row = self.raw_strings[-1]
                if last_row.endswith('"'):
                    self.raw_strings.pop()
                    self.write('{}\\n"'.format(last_row[:-1]))

                self.write(')')
            else:
                self.write('(')
                for pos_arg_index, pos_arg in enumerate(pos_args, 1):
                    self.walk(pos_arg)
                    if pos_arg_index < len(pos_args):
                        self.write(', ')

                self.write(')')
        else:
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

    def process_binary_op(self, operand_left, operator: str, operand_right, is_need_brackets: bool):
        if operator == '**':
            self.raw_imports.add(self.STR_INCLUDE_MODULE_MATH)
            self.write_lbracket(is_need_brackets)
            self.write(f'pow(')
            self.walk(operand_left)
            self.write(f', ')
            self.walk(operand_right)
            self.write(f')')
            self.write_rbracket(is_need_brackets)
            # if not is_need_brackets:
            #     self.write(f';')
        else:
            if operator == '//':  # https://youngcoder.ru/lessons/4/
                operator = '/'

            self.write_lbracket(is_need_brackets)
            self.walk(operand_left)
            self.write(f' {operator} ')
            self.walk(operand_right)
            self.write_rbracket(is_need_brackets)

    def process_unary_op(self, operand, operator: str):
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

    def walk_throw_module(self, module_name):
        modules_dir = self.config.get('modules_dir')
        if modules_dir:
            module_path = modules_dir / f'{module_name}.py'
            if module_path.exists() and module_path.is_file():
                from py2c import bytecode_walker
                translater = TranslatorC(save_to=None)
                translater._walk = self._walk
                with open(module_path) as module_file:
                    bytecode_walker.translate(translater, module_file.read(), save_result=False)

                self.variables_data.update(translater.variables_data)

    def process_import_from(self, module_name: str, imported_objects: list[tuple[str]], level: int):
        module_name = module_name.replace('.', '/')
        if level == 0:
            self.walk_throw_module(module_name)
            self.raw_imports.add(self.STR_INCLUDE_USER_MODULE.format(parent_path='', module_name=module_name))
        else:
            parent_path = '' if level == 1 else '../'*(level-1)
            self.walk_throw_module(module_name)
            self.raw_imports.add(
                self.STR_INCLUDE_USER_MODULE.format(parent_path=parent_path, module_name=module_name),
            )

    def process_import(self, module_names: list[tuple[str]]):
        for module_name, module_alias in module_names:
            module_name = module_name.replace('.', '/')
            self.walk_throw_module(module_name)
            self.raw_imports.add(self.STR_INCLUDE_USER_MODULE.format(parent_path='', module_name=module_name))

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

    def process_compare(self, operand_left, operators: list[tuple[str]], operands_right):
        self.walk(operand_left)
        for operator, operand_right in zip(operators, operands_right):
            self.write(f' {operator} ')
            self.walk(operand_right)

    def process_bool_op(self, operand_left, operator: str, operands_right, is_need_brackets: bool):
        self.write_lbracket(is_need_brackets)
        self.walk(operand_left)
        for operand_right in operands_right:
            self.write(f' {operator} ')
            self.walk(operand_right)

        self.write_rbracket(is_need_brackets)

    def process_break(self, has_while_orelse: bool):
        if has_while_orelse:
            self.write(f'{self.ident}success = 0;\n')

        self.write(f'{self.ident}break;\n')

    def process_ifexpr(self, condition, body, orelse, is_need_brackets: bool):
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

    def process_attribute(self, value, attribute: str):
        if attribute == 'link':
            self.write('&')
            self.walk(value)
        else:
            self.walk(value)

            module_name = 'math'
            if self.raw_strings[-1] == module_name:
                #self.raw_imports.add(f'#include <{module_name}.h>')
                self.raw_strings.pop()
                self.write(f'{attribute}')
            else:
                self.write(f'.{attribute}')

    def process_lambda(self, args: list[str], body):  # only for #define. TODO: build functions for another cases
        self.write('({}) '.format(','.join(args)))
        self.walk(body)

    def process_subscript(self, variable, index):
        self.walk(variable)
        self.write('[')
        self.walk(index)
        self.write(']')

    def process_array(self, elements, variable_name: str):
        if variable_name:
            self.set_variable_data(variable_name, array_sizes=[''])

        self.write('{')
        for index, element in enumerate(elements, 1):
            self.walk(element)
            if index < len(elements):
                self.write(', ')

        self.write('}')

    def process_for_function(self, name: str, body, function_name, args):
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
