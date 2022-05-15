"""
1.  ast.Num, ast.Str - for Python < 3.8. ast.Num.n = ast.Constant.value
"""

import ast
from itertools import chain


class SourceCodeException(Exception):
    def __repr__(self):
        message, node = self.args
        lineno = node.lineno if hasattr(node, 'lineno') else None
        col_offset = node.col_offset if hasattr(node, 'col_offset') else '-'
        name = node.name if hasattr(node, 'name') else '-'
        return f'{message}! Line: {lineno}/{col_offset} Name: {name}'


class TranslateAlgorythmException(Exception):
    pass


class CConverter:
    def __init__(self, save_to):
        self.save_to = save_to
        self.level = 0

        self.col_offset = None
        self.lineno = None
        self._walk = None

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
        self.write(f'{self.ident}{annotation} ')
        name()
        if value is not None:
            self.write(' = ')
            value()

        self.write(';\n')

    def process_assign_variable(self, name, value):
        self.write(self.ident)
        name()
        self.write(' = ')
        value()
        self.write(';\n')

    def process_augassign_variable(self, name, value, operator):
        self.write(self.ident)
        name()
        self.write(f' {operator}= ')
        value()
        self.write(';\n')

    def process_def_function(self, name, annotation, pos_args, body):
        self.write(f'{self.ident}{annotation} {name}(')
        str_args = [f'{annotation_arg} {name_arg}' for annotation_arg, name_arg in pos_args]
        self.write(', '.join(str_args) if pos_args else 'void')
        self.write(') {\n')
        for expression in body:
            self.walk(expression, 1)

        self.write('}\n')

    def process_call_function(self, name, pos_args):
        name()
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
        operand_left()
        self.write(f' {operator} ')
        operand_right()

    def process_unary_op(self, operand, operator):
        self.write(f' {operator}')
        operand()

    def process_return(self, expression):
        self.write(f'{self.ident}return ')
        expression()
        self.write(';\n')

    def process_while(self, condition, body, orelse):
        if orelse:
            self.write(f'{self.ident}unsigned byte success = 1;\n')

        self.write(f'{self.ident}while (')
        condition()
        self.write(') {\n')
        self.level += 1
        body()
        self.level -= 1
        self.write(f'{self.ident}}}\n\n')

        self.write(f'{self.ident}if (success == 1) {{\n')
        for expression in orelse:
            self.walk(expression, 1)

        self.write(f'{self.ident}}}\n\n')

    def process_import_from(self, module_name, imported_objects):
        self.write(f'#include <{module_name}.h>\n\n')

    def process_import(self, module_names):
        for module_name in module_names:
            self.write(f'#include <{module_name}.h>\n')

        self.write('\n')

    def process_expression(self, expression):
        self.write(self.ident)
        expression()
        self.write(';\n')

    def process_if(self, condition, body, orelse):
        self.write(f'{self.ident}if (')
        condition()
        self.write(') {\n')
        self.level += 1
        body()
        self.level -= 1
        self.write(f'{self.ident}}}')

        if orelse:
            self.write(' else ')
            self.write('{\n')
            self.level += 1
            orelse()
            self.level -= 1
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
    #elif isinstance(node, ast.FloorDiv):
    #    return ''
    #elif isinstance(node, ast.Mod):
    #    return ''
    #elif isinstance(node, ast.Pow):
    #    return ''
    #elif isinstance(node, ast.RShift):
    #    return ''
    #elif isinstance(node, ast.LShift):
    #    return ''
    elif isinstance(node, ast.BitOr):
        return '|'
    elif isinstance(node, ast.BitXor):
        return '^'
    elif isinstance(node, ast.BitAnd):
        return '&'
    #elif isinstance(node, ast.MatMult):
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
    #elif isinstance(node, ast.Is):
    #    return ''
    #elif isinstance(node, ast.IsNot):
    #    return ''
    #elif isinstance(node, ast.In):
    #    return ''
    #elif isinstance(node, ast.NotIn):
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

    raise SourceCodeException('unknown annotation node', node)


def walk(converter, parent_node, has_while_orelse=None, for_ifexpr=None):
    if parent_node is None:
        #converter.write('None')
        return

    if has_while_orelse is None:
        has_while_orelse = []

    for node in chain([parent_node], ast.iter_child_nodes(parent_node)):
        if hasattr(node, 'custom_ignore') and node.custom_ignore:
            continue

        converter.lineno = node.lineno if hasattr(node, 'lineno') else converter.lineno
        converter.col_offset = node.col_offset if hasattr(node, 'col_offset') else converter.col_offset
        node.lineno = converter.lineno
        node.col_offset = converter.col_offset

        node.custom_ignore = True
        if isinstance(node, ast.AnnAssign):
            value = None
            if node.value and not is_constant_none(node):
                value = lambda: walk(converter, node.value)

            converter.process_init_variable(
                name=lambda: walk(converter, node.target),
                value=value,
                annotation=convert_annotation(node.annotation, node),
            )

        elif isinstance(node, ast.Assign):
            if isinstance(node.value, ast.IfExp):
                data = {'target': node.targets[0], 'value': None}
                walk(converter, node.value, for_ifexpr=data)
                data['target'].custom_ignore = False
                node.value = data['value']

            for target in node.targets:
                node.value.custom_ignore = False
                converter.process_assign_variable(
                    name=lambda: walk(converter, target),
                    value=lambda: walk(converter, node.value),
                )

        elif isinstance(node, ast.AugAssign):
            converter.process_augassign_variable(
                name=lambda: walk(converter, node.target),
                value=lambda: walk(converter, node.value),
                operator=convert_op(node.op),
            )

        elif isinstance(node, ast.FunctionDef):
            pos_args = []
            for arg in node.args.args:
                ann_name = convert_annotation(arg.annotation, node)
                pos_args.append((ann_name, arg.arg))

            converter.process_def_function(
                name=node.name,
                annotation=convert_annotation(node.returns, node),
                pos_args=pos_args,
                body=node.body,
            )

        elif isinstance(node, ast.Call):  # TODO: обрабатывать другие виды аргуентов
            pos_args = []
            for arg_node in node.args:
                pos_args.append(arg_node)

            # for keyword in node.keywords:
            #     #walk(arg)
            #     converter.write(', ')

            converter.process_call_function(
                name=lambda: walk(converter, node.func),
                pos_args=pos_args,
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
                operand_left=lambda: walk(converter, node.left),
                operator=convert_op(node.op),
                operand_right=lambda: walk(converter, node.right),
            )

        elif isinstance(node, ast.BoolOp):
            converter.process_bool_op(
                operand_left=node.values[0],
                operator=convert_bool_op(node.op),
                operands_right=node.values[1:],
            )

        elif isinstance(node, ast.UnaryOp):
            converter.process_unary_op(
                operand=lambda: walk(converter, node.operand),
                operator=convert_unary_op(node.op),
            )

        elif isinstance(node, ast.Return):
            #if node.value:
            converter.process_return(
                expression=lambda: walk(converter, node.value),
            )

        elif isinstance(node, ast.NameConstant):  # New in version 3.4; Deprecated since version 3.8
            walk(converter, node.value)

        elif isinstance(node, ast.IfExp):
            target = ast.AnnAssign(
                target=ast.Name(id='success', ctx=ast.Store),
                annotation=ast.Name(id='unsigned int', ctx=ast.Load),
                value=None,
            )
            walk(converter, target)

            converter.write('    ' * converter.level)
            converter.write('if (')
            walk(converter, node.test)
            converter.write(') {\n')
            converter.write('    ' * (converter.level+1))
            # if for_ifexpr:
            #     walk(for_ifexpr)

            target = ast.Assign(
                targets=[ast.Name(id='success', ctx=ast.Store)],
                value=node.body,
            )
            walk(converter, target)
            # converter.write(';\n')
            converter.write('    ' * converter.level)
            converter.write('} else {\n')
            converter.write('    ' * (converter.level+1))
            # if for_ifexpr:
            #     for_ifexpr.custom_ignore = False
            #     walk(for_ifexpr)

            target = ast.Assign(
                targets=[ast.Name(id='success', ctx=ast.Store)],
                value=node.orelse,
            )
            walk(converter, target)
            # converter.write(';\n')
            converter.write('    ' * converter.level)
            converter.write('}\n\n')
            for_ifexpr['value'] = ast.Name(id='success', ctx=ast.Load)

        elif isinstance(node, ast.If):
            def body():
                for node_body in node.body:
                    walk(converter, node_body, has_while_orelse)

            def orelse():
                for node_orelse in node.orelse:
                    walk(converter, node_orelse, has_while_orelse)

            # if node.orelse:
            #     if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            #         walk(converter, node.orelse[0], has_while_orelse)


            converter.process_if(
                condition=lambda: walk(converter, node.test),
                body=body,
                orelse=orelse,
            )

        elif isinstance(node, ast.While):
            def body():
                for node_body in node.body:
                    # TODO: перед опретаором break необходимо выполнить код "success=0;".
                    walk(converter, node_body, has_while_orelse+[bool(node.orelse)])

            converter.process_while(
                condition=lambda: walk(converter, node.test),
                body=body,
                orelse=node.orelse,
            )

        elif isinstance(node, ast.Break):
            if has_while_orelse[-1]:
                converter.write('    ' * converter.level)
                converter.write('success = 0;\n')

            converter.write('    ' * converter.level)
            converter.write('break;\n')

        elif isinstance(node, ast.Continue):
            converter.process_continue()

        elif isinstance(node, ast.Expr):
            converter.process_expression(
                expression=lambda: walk(converter, node.value),
            )

        elif isinstance(node, (ast.Pass, ast.Module)):
            pass

        elif isinstance(node, ast.Import):
            converter.process_import([node_name.name for node_name in node.names])

        elif isinstance(node, ast.ImportFrom):
            converter.process_import_from(node.module, None)

        elif isinstance(node, ast.Compare):
            converter.process_compare(node.left, [convert_compare_op(op) for op in node.ops], node.comparators)

        else:
            raise SourceCodeException(f'unknown node: {node.__class__.__name__} {str(parent_node)}', node)


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
