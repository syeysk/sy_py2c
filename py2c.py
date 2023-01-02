import ast
from dataclasses import dataclass, field
from typing import Optional, List, Tuple


class SourceCodeException(Exception):
    def __init__(self, message, node):
        lineno = node.lineno if hasattr(node, 'lineno') else None
        col_offset = node.col_offset if hasattr(node, 'col_offset') else '-'
        name = node.__class__.__name__  # node.name if hasattr(node, 'name') else '-'
        message = f'{message}! Line: {lineno}/{col_offset} Name: {name}'
        super().__init__(message)


class InvalidAnnotationException(SourceCodeException):
    pass


class NoneIsNotAllowedException(SourceCodeException):
    pass


class UnsupportedImportException(SourceCodeException):
    pass


class LambdaIsNotAllowedHereException(SourceCodeException):
    pass


class TranslateAlgorythmException(Exception):
    pass


@dataclass
class Annotation:
    type: str
    array_sizes: List[str] = field(default_factory=list)
    link: bool = False


class CConverter:
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
        self.raw_imports = []

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
        str_imports = '\n'.join(self.raw_imports)
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
        self.raw_imports.append(f'#include <{module_name}>')
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
            self.raw_imports.append(f'#include <{module_name}.h>')
        else:
            parent_path = './' if level == 1 else '../'*(level-1)
            self.raw_imports.append(f'#include "{parent_path}{module_name}.h"')

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


def convert_op(node):
    node.custom_ignore = True
    if isinstance(node, ast.Add):
        return '+'
    elif isinstance(node, ast.Sub):
        return '-'
    elif isinstance(node, ast.Mult):
        return '*'
    elif isinstance(node, ast.Div):
        return '/'
    # elif isinstance(node, ast.FloorDiv):
    #    return ''
    elif isinstance(node, ast.Mod):
        return '%'
    # elif isinstance(node, ast.Pow):
    #    return ''
    elif isinstance(node, ast.RShift):
        return '>>'
    elif isinstance(node, ast.LShift):
        return '<<'
    elif isinstance(node, ast.BitOr):
        return '|'
    elif isinstance(node, ast.BitXor):
        return '^'
    elif isinstance(node, ast.BitAnd):
        return '&'
    # elif isinstance(node, ast.MatMult):
    #    return ''
    else:
        raise SourceCodeException('unknown node operator', node)


def convert_compare_op(node):
    node.custom_ignore = True
    if isinstance(node, ast.Gt):
        return '>'
    elif isinstance(node, ast.GtE):
        return '>='
    elif isinstance(node, ast.Lt):
        return '<'
    elif isinstance(node, ast.LtE):
        return '<='
    elif isinstance(node, ast.Eq):
        return '=='
    elif isinstance(node, ast.NotEq):
        return '!='
    # elif isinstance(node, ast.Is):
    #    return ''
    # elif isinstance(node, ast.IsNot):
    #    return ''
    # elif isinstance(node, ast.In):
    #    return ''
    # elif isinstance(node, ast.NotIn):
    #    return ''
    else:
        raise SourceCodeException('unknown node compare operator', node)


def convert_bool_op(node):
    node.custom_ignore = True
    if isinstance(node, ast.Or):
        return '||'
    elif isinstance(node, ast.And):
        return '&&'
    else:
        raise SourceCodeException('unknown node bool operator', node)


def convert_unary_op(node):
    node.custom_ignore = True
    if isinstance(node, ast.UAdd):
        return '+'
    elif isinstance(node, ast.USub):
        return '-'
    elif isinstance(node, ast.Not):
        return '!'
    elif isinstance(node, ast.Invert):
        return '~'
    else:
        raise SourceCodeException('unknown node unary operator', node)


def convert_annotation(annotation_node, parent_node) -> Optional[str]:
    # # закомментирован, так как переменные могут быть объявлены в C-библиотеках
    # if not allow_absent and annotation_node is None:
    #     raise SourceCodeException('annotation must be!', parent_node)
    if annotation_node is None:
        return

    annotation_node.custom_ignore = True
    if isinstance(annotation_node, ast.Name):
        return annotation_node.id
    elif isinstance(annotation_node, ast.Constant):
        if annotation_node.value is None:
            raise NoneIsNotAllowedException('None is forbidden', parent_node)

        return annotation_node.value
    elif isinstance(annotation_node, ast.Num):
        return annotation_node.n
    elif isinstance(annotation_node, ast.Str):
        return annotation_node.s
    elif isinstance(annotation_node, ast.NameConstant):  # Python 3.4 - 3.8
        if annotation_node.value is None:
            raise NoneIsNotAllowedException('None is forbidden', parent_node)

        return convert_annotation(annotation_node.value, parent_node)

    raise InvalidAnnotationException('unknown annotation node', annotation_node)


def walk(converter, node):
    if node is None or getattr(node, 'custom_ignore', False):
        return

    parents = converter.transit_data.setdefault('parents', [])
    parent_node = parents[-1] if parents else None
    parents.append(node)

    has_while_orelse = converter.transit_data.setdefault('has_while_orelse', [])

    converter.lineno = node.lineno if hasattr(node, 'lineno') else converter.lineno
    converter.col_offset = node.col_offset if hasattr(node, 'col_offset') else converter.col_offset
    node.lineno = converter.lineno
    node.col_offset = converter.col_offset

    node.custom_ignore = True
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.value, ast.Lambda):
            lambda_node = node.value
            lambda_node.custom_ignore = True
            args = [arg.arg for arg in lambda_node.args.args]
            body = lambda_node.body
            value_expr = None
            value_lambda = (args, body)
        else:
            value_expr = node.value
            value_lambda = None

        converter.process_init_variable(
            name=node.target,
            value_expr=value_expr,
            annotation=convert_annotation(node.annotation, node),
            value_lambda=value_lambda,
        )

    elif isinstance(node, ast.Assign):
        # if isinstance(node.value, ast.IfExp):
        #     data = {'targets': node.targets, 'value': None}
        #     walk(converter, node.value, for_ifexpr=data)
        #     node.value = data['value']

        converter.process_assign_variable(
            names=node.targets,
            value=node.value,
        )

    elif isinstance(node, ast.AugAssign):
        converter.process_augassign_variable(
            name=node.target,
            value=node.value,
            operator=convert_op(node.op),
        )

    elif isinstance(node, ast.FunctionDef):
        pos_args = []
        for index_arg, arg in enumerate(node.args.args):  # node.args is ast.arguments
            ann_name = convert_annotation(arg.annotation, node)
            pos_arg = (ann_name, arg.arg)
            pos_args.append(pos_arg)

        docstring_comment = ast.get_docstring(node)
        if docstring_comment is not None:
            node.body[0].custom_ignore = True
            node.body[0].value.custom_ignore = True

        converter.process_def_function(
            name=node.name,
            annotation=convert_annotation(node.returns, node),
            pos_args=pos_args,
            pos_args_defaults=node.args.defaults,
            body=node.body,
            docstring_comment=docstring_comment,
        )

    elif isinstance(node, ast.Call):  # TODO: обрабатывать другие виды аргуентов
        converter.process_call_function(
            name=node.func,
            pos_args=node.args,
        )

    elif isinstance(node, ast.Constant):
        converter.process_constant(node.value, node)

    elif isinstance(node, ast.Num):  # Deprecated since version 3.8
        converter.process_constant(node.n, node)

    elif isinstance(node, ast.Str):  # Deprecated since version 3.8
        converter.process_constant(node.s, node)

    elif isinstance(node, ast.Name):
        converter.process_name(node.id)
        node.ctx.custom_ignore = True  # we ignore ast.Load, ast.Store and ast.Del

    elif isinstance(node, (ast.Load, ast.Store, ast.Del)):
        pass

    elif isinstance(node, ast.Delete):
        names = []
        for target_node in node.targets:
            names.append(target_node)

        converter.process_delete_variable(names)

    elif isinstance(node, ast.BinOp):
        is_need_brackets = isinstance(parent_node, (ast.BinOp, ast.UnaryOp))
        if isinstance(node.op, ast.Pow):
            converter.process_binary_op_pow(
                operand_left=node.left,
                operand_right=node.right,
                is_need_brackets=is_need_brackets,
            )
        else:
            converter.process_binary_op(
                operand_left=node.left,
                operator=convert_op(node.op),
                operand_right=node.right,
                is_need_brackets=is_need_brackets,
            )

    elif isinstance(node, ast.BoolOp):
        is_need_brackets = isinstance(parent_node, (ast.BoolOp, ast.UnaryOp))
        converter.process_bool_op(
            operand_left=node.values[0],
            operator=convert_bool_op(node.op),
            operands_right=node.values[1:],
            is_need_brackets=is_need_brackets,
        )

    elif isinstance(node, ast.UnaryOp):
        converter.process_unary_op(
            operand=node.operand,
            operator=convert_unary_op(node.op),
        )

    elif isinstance(node, ast.Return):
        if isinstance(node.value, ast.Tuple):
            converter.process_multi_return(expressions=node.value)
        else:
            converter.process_return(expression=node.value)

    elif isinstance(node, ast.NameConstant):  # New in version 3.4; Deprecated since version 3.8
        if isinstance(node.value, bool):
            converter.process_constant(node.value, node)
        else:
            walk(converter, node.value)

    elif isinstance(node, ast.IfExp):
        is_need_brackets = isinstance(parent_node, (ast.Call, ast.BoolOp))
        converter.process_ifexpr(
            condition=node.test,
            body=node.body,
            orelse=node.orelse,
            is_need_brackets=is_need_brackets,
        )

    # Control flow

    elif isinstance(node, ast.If):
        ifelses = []
        orelse = node.orelse
        while orelse and len(orelse) == 1 and isinstance(orelse[0], ast.If):
            ifelses.append((orelse[0].test, orelse[0].body))
            orelse = orelse[0].orelse
            node.orelse = None

        converter.process_if(
            condition=node.test,
            body=node.body,
            ifelses=ifelses,
            orelse=orelse,
        )

    elif isinstance(node, ast.For):
        if isinstance(node.target, ast.Name):
            name = node.target.id
        else:
            raise Exception('Unsupported target of `for`!')

        if isinstance(node.iter, ast.Call):
            converter.process_for_function(name, node.body, node.iter.func.id, node.iter.args)
        else:
            raise Exception('Unsupported iter of `for`!')

    elif isinstance(node, ast.While):
        has_while_orelse.append(bool(node.orelse))
        converter.process_while(
            condition=node.test,
            body=node.body,
            orelse=node.orelse,
        )
        has_while_orelse.pop()

    elif isinstance(node, ast.Break):
        converter.process_break(has_while_orelse[-1])

    elif isinstance(node, ast.Continue):
        converter.process_continue()

    elif isinstance(node, ast.Expr):
        if isinstance(node.value, (ast.Str, ast.Constant)) and isinstance(parent_node, ast.Module):
            comment = ''
            if isinstance(node.value, ast.Str):
                comment = node.value.s
            elif isinstance(node.value, ast.Constant):
                comment = node.value.value

            if '\n' in comment:
                converter.process_multiline_comment(comment)
            else:
                converter.process_one_comment(comment)
        else:
            converter.process_expression(
                expression=node.value,
            )

    elif isinstance(node, ast.Pass):
        pass

    elif isinstance(node, ast.Import):
        converter.process_import([node_name.name for node_name in node.names])

    elif isinstance(node, ast.ImportFrom):
        names = [(alias.name, alias.asname) for alias in node.names]
        converter.process_import_from(node.module, names, node.level)

    elif isinstance(node, ast.Compare):
        converter.process_compare(node.left, [convert_compare_op(op) for op in node.ops], node.comparators)

    elif isinstance(node, ast.Attribute):
        if node.attr == 'link':
            converter.process_link(node.value)

    elif isinstance(node, ast.Lambda):
        pos_args = []
        node.args.custom_ignore = True
        for arg in node.args.args:  # node.args is ast.arguments
            pos_args.append(arg.arg)

        converter.process_lambda(pos_args, node.body)

    # Subscripting
    elif isinstance(node, ast.Subscript):
        index = None
        if isinstance(node.slice, ast.Index):  # ast.Index is for Python <=3.8;
            node.slice.custom_ignore = True
            index = node.slice.value
        elif isinstance(node.slice, ast.Constant):  # ast.Constant is for Python >= 3.9
            index = node.slice
        elif isinstance(node.slice, ast.Name):  # ast.Constant is for Python >= 3.9
            index = node.slice
        else:
            raise SourceCodeException('Unknown index node', node.slice)

        converter.process_subscript(node.value, index)

    # elif isinstance(node, ast.Slice):
    # elif isinstance(node, ast.ExtSlice):

    # Top level nodes
    elif isinstance(node, ast.Module):
        for body_node in node.body:
            walk(converter, body_node)

    # elif isinstance(node, ast.Interactive):
    # elif isinstance(node, ast.Expression):

    # Literals
    elif isinstance(node, ast.List):
        converter.process_array(node.elts)

    elif isinstance(node, ast.Tuple):
        converter.process_array(node.elts)
    #     if isinstance(parent_node, ast.Return):
    #         converter.process_multi_return(expressions=node.elts)
    #     else:
    #         raise SourceCodeException(f'unknown node: {node.__class__.__name__}', node)

    else:
        raise SourceCodeException(f'unknown node: {node.__class__.__name__}', node)

    if parents:
        parents.pop()


def main(converter, source_code):
    converter._walk = walk
    tree = ast.parse(source_code)
    walk(converter, tree)
    converter.save()
