import ast
from itertools import chain


class SourceCodeException(Exception):
    def __repr__(self):
        message, node = self.args
        lineno = node.lineno if hasattr(node, 'lineno') else None
        col_offset = node.col_offset if hasattr(node, 'col_offset') else '-'
        name = node.__class__.__name__  # node.name if hasattr(node, 'name') else '-'
        return f'{message}! Line: {lineno}/{col_offset} Name: {name}'


class TranslateAlgorythmException(Exception):
    pass


class CConverter:
    def __init__(self, save_to, config=None):
        self.config = {} if config is None else config
        self.save_to = save_to
        self.level = 0

        self.col_offset = None
        self.lineno = None
        self._walk = None
        self.transit_data = {}

    def write(self, data: str):
        self.save_to.write(data)

    @property
    def ident(self):
        return '    ' * self.level

    def walk(self, node, level=0):
        self.level += level
        self._walk(self, node)
        self.level -= level

    def process_init_variable(self, name, value, annotation):
        if annotation == 'const':
            self.write(f'#define ')
            self.walk(name)
            if value is None:
                raise SourceCodeException('Constanta must have a value!', node)

            self.write(' ')
            self.walk(value)
            self.write('\n')
        else:
            self.write(f'{self.ident}{annotation} ')
            self.walk(name)
            if value is not None:
                self.write(' = ')
                self.walk(value)

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

    def process_def_function(self, name, annotation, pos_args, body, desrciption_comment):
        if desrciption_comment:
            self.write(f'{self.ident}/*\n')
            for line in desrciption_comment.split('\n'):
                self.write(f'{self.ident}{line}\n')

            self.write(f'{self.ident}*/\n')

        self.write(f'{self.ident}{annotation} {name}(')
        str_args = [f'{annotation_arg} {name_arg}' for annotation_arg, name_arg in pos_args]
        self.write(', '.join(str_args) if pos_args else 'void')
        self.write(') {\n')
        for expression in body:
            self.walk(expression, 1)

        self.write('}\n')

    def process_call_function(self, name, pos_args):
        self.walk(name)
        self.write(f'(')
        for pos_arg_index, pos_arg in enumerate(pos_args, 1):
            self.walk(pos_arg)
            if pos_arg_index < len(pos_args):
                self.write(', ')

        self.write(')')

    def process_constant(self, value):
        if value is None:
            self.write('NULL')  # для указателей
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

    def process_binary_op(self, operand_left, operator, operand_right):
        self.walk(operand_left)
        self.write(f' {operator} ')
        self.walk(operand_right)

    def process_unary_op(self, operand, operator):
        self.write(f' {operator}')
        self.walk(operand)

    def process_return(self, expression):
        self.write(f'{self.ident}return ')
        self.walk(expression)
        self.write(';\n')

    def process_while(self, condition, body, orelse):
        if orelse:
            self.write(f'{self.ident}unsigned byte success = 1;\n')

        self.write(f'{self.ident}while (')
        self.walk(condition)
        self.write(') {\n')
        for expression in body:
            self.walk(expression, 1)

        self.write(f'{self.ident}}}\n\n')

        self.write(f'{self.ident}if (success == 1) {{\n')
        for expression in orelse:
            self.walk(expression, 1)

        self.write(f'{self.ident}}}\n\n')

    def process_import_from(self, module_name, imported_objects):
        module_name = module_name.replace('.', '/')
        self.write(f'#include <{module_name}.h>\n\n')

    def process_import(self, module_names):
        for module_name in module_names:
            module_name = module_name.replace('.', '/')
            self.write(f'#include <{module_name}.h>\n')

        self.write('\n')

    def process_expression(self, expression):
        self.write(self.ident)
        self.walk(expression)
        self.write(';\n')

    def process_if(self, condition, body, orelse):
        self.write(f'{self.ident}if (')
        self.walk(condition)
        self.write(') {\n')
        for expression in body:
            self.walk(expression, 1)

        self.write(f'{self.ident}}}')

        if orelse:
            self.write(' else ')
            self.write('{\n')
            for expression in orelse:
                self.walk(expression, 1)

            self.write(f'{self.ident}}}\n\n')
        else:
            self.write('\n\n')

    def process_compare(self, operand_left, operators, operands_right):
        self.walk(operand_left)
        for operator, operand_right in zip(operators, operands_right):
            self.write(f' {operator} ')
            self.walk(operand_right)

    def process_bool_op(self, operand_left, operator, operands_right):
        self.walk(operand_left)
        self.write(f' {operator} ')
        for operand_right in operands_right:
            self.walk(operand_right)

    def process_break(self, has_while_orelse):
        if has_while_orelse:
            self.write(f'{self.ident}success = 0;\n')

        self.write(f'{self.ident}break;\n')

    def process_ifexpr(self, condition, body, orelse):
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

        self.write('(')
        self.walk(condition)
        self.write(') ? ')
        self.walk(body)
        self.write(' : ')
        self.walk(orelse)

    def process_link(self, value):
        self.write('&')
        self.walk(value)

    def process_lambda(self, args, body):  # only for #define. TODO: build functions for anothes cases
        self.write('({}) '.format(', '.join(args)))
        self.walk(body)

    def process_subscript(self, variable, index):
        self.walk(variable)
        self.write('[')
        self.walk(index)
        self.write(']')


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
    # elif isinstance(node, ast.RShift):
    #    return ''
    # elif isinstance(node, ast.LShift):
    #    return ''
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


def is_constant_none(node):
    return isinstance(node, (ast.Constant, ast.Num, ast.Str)) and node.value is None


def convert_annotation(node, parent_node):
    if node is None:
        if isinstance(parent_node, ast.FunctionDef):
            return 'void'

        raise SourceCodeException('annotation must be!', parent_node)

    node.custom_ignore = True
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.NameConstant):  # Python 3.4 - 3.8
        return convert_annotation(node.value, parent_node)

    raise SourceCodeException('unknown annotation node', node)


def walk(converter, parent_node):
    if parent_node is None:
        # converter.write('None')
        return

    has_while_orelse = converter.transit_data.setdefault('has_while_orelse', [])

    for node in chain([parent_node], ast.iter_child_nodes(parent_node)):
        if hasattr(node, 'custom_ignore') and node.custom_ignore:
            continue

        converter.lineno = node.lineno if hasattr(node, 'lineno') else converter.lineno
        converter.col_offset = node.col_offset if hasattr(node, 'col_offset') else converter.col_offset
        node.lineno = converter.lineno
        node.col_offset = converter.col_offset

        node.custom_ignore = True
        if isinstance(node, ast.AnnAssign):
            converter.process_init_variable(
                name=node.target,
                value=node.value if node.value and not is_constant_none(node) else None,
                annotation=convert_annotation(node.annotation, node),
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
            for arg in node.args.args:  # node.args is ast.arguments
                ann_name = convert_annotation(arg.annotation, node)
                pos_args.append((ann_name, arg.arg))

            desrciption_comment = None
            if hasattr(node, 'type_comment'):  # for Python 3.8 and upper
                desrciption_comment = node.type_comment
            else:
                first_node = node.body[0] if node.body else None
                if first_node and isinstance(first_node, ast.Expr):
                    if isinstance(first_node.value, ast.Str):
                        first_node.custom_ignore = True
                        first_node.value.custom_ignore = True
                        desrciption_comment = first_node.value.s
                    elif isinstance(first_node.value, ast.Constant):
                        first_node.custom_ignore = True
                        first_node.value.custom_ignore = True
                        desrciption_comment = first_node.value.value

            converter.process_def_function(
                name=node.name,
                annotation=convert_annotation(node.returns, node),
                pos_args=pos_args,
                body=node.body,
                desrciption_comment=desrciption_comment,
            )

        elif isinstance(node, ast.Call):  # TODO: обрабатывать другие виды аргуентов
            converter.process_call_function(
                name=node.func,
                pos_args=node.args,
            )

        elif isinstance(node, ast.Constant):
            converter.process_constant(node.value)

        elif isinstance(node, ast.Num):  # Deprecated since version 3.8
            converter.process_constant(node.n)

        elif isinstance(node, ast.Str):  # Deprecated since version 3.8
            converter.process_constant(node.s)

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
            converter.process_binary_op(
                operand_left=node.left,
                operator=convert_op(node.op),
                operand_right=node.right,
            )

        elif isinstance(node, ast.BoolOp):
            converter.process_bool_op(
                operand_left=node.values[0],
                operator=convert_bool_op(node.op),
                operands_right=node.values[1:],
            )

        elif isinstance(node, ast.UnaryOp):
            converter.process_unary_op(
                operand=node.operand,
                operator=convert_unary_op(node.op),
            )

        elif isinstance(node, ast.Return):
            # if node.value:
            converter.process_return(
                expression=node.value,
            )

        elif isinstance(node, ast.NameConstant):  # New in version 3.4; Deprecated since version 3.8
            walk(converter, node.value)

        elif isinstance(node, ast.IfExp):
            # process_assign_variable
            # if not for_ifexpr:
            # target = ast.AnnAssign(
            #     target=ast.Name(id='temp', ctx=ast.Store),
            #     annotation=ast.Name(id='unsigned int', ctx=ast.Load),
            #     value=None,
            # )
            # walk(converter, target)

            # walk(converter, node.test)

            # targets = for_ifexpr['targets'] if for_ifexpr else [ast.Name(id='temp', ctx=ast.Store)]
            # for target in targets:
            #     target.custom_ignore = False

            # target = ast.Assign(targets=targets, value=node.body)
            # walk(converter, target)
            # for target in targets:
            #     target.custom_ignore = False
            #
            # target = ast.Assign(targets=targets, value=node.orelse)
            # walk(converter, target)
            # for_ifexpr['value'] = ast.Name(id='temp', ctx=ast.Load)

            converter.process_ifexpr(
                condition=node.test,
                body=node.body,
                orelse=node.orelse,
            )

        elif isinstance(node, ast.If):
            # if node.orelse:
            #     if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            #         walk(converter, node.orelse[0])

            converter.process_if(
                condition=node.test,
                body=node.body,
                orelse=node.orelse,
            )

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
            converter.process_expression(
                expression=node.value,
            )

        elif isinstance(node, (ast.Pass, ast.Module)):
            pass

        elif isinstance(node, ast.Import):
            converter.process_import([node_name.name for node_name in node.names])

        elif isinstance(node, ast.ImportFrom):
            converter.process_import_from(node.module, None)

        elif isinstance(node, ast.Compare):
            converter.process_compare(node.left, [convert_compare_op(op) for op in node.ops], node.comparators)

        elif isinstance(node, ast.Attribute):
            if node.attr == 'link':
                converter.process_link(node.value)

        elif isinstance(node, ast.Lambda):
            pos_args = []
            node.args.custom_ignore = True
            for arg in node.args.args:  # node.args is ast.arguments
                # ann_name = convert_annotation(arg.annotation, node)
                # pos_args.append((ann_name, arg.arg))
                pos_args.append(arg.arg)

            converter.process_lambda(pos_args, node.body)

        # Subscripting
        elif isinstance(node, ast.Subscript):
            index = None
            if isinstance(node.slice, ast.Index):
                node.slice.custom_ignore = True
                index = node.slice.value

            converter.process_subscript(node.value, index)

        # elif isinstance(node, ast.Slice):
        # elif isinstance(node, ast.ExtSlice):

        else:
            raise SourceCodeException(f'unknown node: {node.__class__.__name__}', node)


def main(converter, source_code):
    converter._walk = walk
    tree = ast.parse(source_code)
    walk(converter, tree)


if __name__ == '__main__':
    import os

    with open('example/example.py') as example_py_file:
        source_code = example_py_file.read()

    with open('example.c', 'w') as example_c_file:
        converter = CConverter(save_to=example_c_file)
        main(converter, source_code)

    path_example_from_book = 'example/from_book/'
    for filepath in os.listdir(path_example_from_book):
        print()
        print(filepath)
        with open(os.path.join(path_example_from_book, filepath)) as example_py_file:
            source_code = example_py_file.read()

        with open(f'{filepath}.c', 'w') as example_c_file:
            converter = CConverter(save_to=example_c_file)
            main(converter, source_code)
