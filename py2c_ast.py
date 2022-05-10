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


def walk(parent_node, save_to, level=0, has_while_orelse=None, for_ifexpr=None, lineno=None, col_offset=None):
    if parent_node is None:
        save_to.write('None')
        return

    if has_while_orelse is None:
        has_while_orelse = []

    for node in chain([parent_node], ast.iter_child_nodes(parent_node)):
        if hasattr(node, 'custom_ignore') and node.custom_ignore:
            continue

        lineno = node.lineno if hasattr(node, 'lineno') else lineno
        col_offset = node.col_offset if hasattr(node, 'col_offset') else col_offset
        node.lineno = lineno
        node.col_offset = col_offset

        node.custom_ignore = True
        if isinstance(node, ast.AnnAssign):
            save_to.write('    '*level)
            ann_name = convert_annotation(node.annotation, node)
            save_to.write(f'{ann_name} ')
            walk(node.target, save_to, level, lineno=lineno, col_offset=col_offset)
            if node.value and not is_constant_none(node):
                save_to.write(' = ')
                walk(node.value, save_to, level, lineno=lineno, col_offset=col_offset)

            save_to.write(';\n')

        elif isinstance(node, ast.Assign):
            if isinstance(node.value, ast.IfExp):
                data = {'target': node.targets[0], 'value': None}
                walk(node.value, save_to, level, for_ifexpr=data, lineno=lineno, col_offset=col_offset)
                data['target'].custom_ignore = False
                node.value = data['value']

            for target in node.targets:
                save_to.write('    ' * level)
                walk(target, save_to, level, lineno=lineno, col_offset=col_offset)
                save_to.write(' = ')
                node.value.custom_ignore = False
                walk(node.value, save_to, level, lineno=lineno, col_offset=col_offset)
                save_to.write(';\n')

        elif isinstance(node, ast.AugAssign):
            save_to.write('    '*level)
            walk(node.target, save_to, level, lineno=lineno, col_offset=col_offset)
            save_to.write(' {}= '.format(convert_op(node.op)))
            walk(node.value, save_to, level, lineno=lineno, col_offset=col_offset)
            save_to.write(';\n')

        elif isinstance(node, ast.FunctionDef):
            save_to.write('    '*level)
            ann_name = convert_annotation(node.returns, node)
            save_to.write(f'{ann_name} {node.name}(')
            str_args = []
            data_args = node.args
            for arg in data_args.args:
                ann_name = convert_annotation(arg.annotation, node)
                str_args.append(f'{ann_name} {arg.arg}')

            save_to.write(', '.join(str_args) if data_args.args else 'void')
            save_to.write(') {\n')
            for node_body in node.body:
                walk(node_body, save_to, level+1, lineno=lineno, col_offset=col_offset)

            save_to.write('}\n')

        elif isinstance(node, ast.Call):  # TODO: обрабатывать другие виды аргуентов
            walk(node.func, save_to, level, lineno=lineno, col_offset=col_offset)
            save_to.write(f'(')
            for arg_index, arg_node in enumerate(node.args, 1):
                walk(arg_node, save_to, level, lineno=lineno, col_offset=col_offset)
                if arg_index < len(node.args):
                    save_to.write(', ')

            for keyword in node.keywords:
                #walk(arg, save_to, level)
                save_to.write(', ')

            save_to.write(')')

        elif isinstance(node, (ast.Constant, ast.Num, ast.Str)):
            value = node.value if isinstance(node, ast.Constant) else (node.n if isinstance(node, ast.Num) else node.s)
            if value is None:
                save_to.write('NULL')  # для указателей
            elif isinstance(value, str):
                save_to.write('"{}"'.format(value))
            elif isinstance(value, bool):
                save_to.write('{}'.format(1 if value else 0))
            elif isinstance(value, (int, float)):
                save_to.write('{}'.format(value))

        elif isinstance(node, ast.Name):
            save_to.write('{}'.format(node.id))
            node.ctx.custom_ignore = True  # we don't use is ast.Load, ast.Store and ast.Del

        elif isinstance(node, ast.Delete):
            for target_node in node.targets:
                save_to.write('delete ')
                walk(target_node, save_to, level, lineno=lineno, col_offset=col_offset)
                save_to.write(';\n')

        elif isinstance(node, ast.BinOp):
            walk(node.left, save_to, level, lineno=lineno, col_offset=col_offset)
            save_to.write(' {} '.format(convert_op(node.op)))
            walk(node.right, save_to, level, lineno=lineno, col_offset=col_offset)

        elif isinstance(node, ast.BoolOp):
            walk(node.values[0], save_to, level, lineno=lineno, col_offset=col_offset)
            for value in node.values[1:]:
                save_to.write(' {} '.format(convert_bool_op(node.op)))
                walk(value, save_to, level, lineno=lineno, col_offset=col_offset)

        elif isinstance(node, ast.UnaryOp):
                save_to.write(' {}'.format(convert_unary_op(node.op)))
                walk(node.operand, save_to, level, lineno=lineno, col_offset=col_offset)

        elif isinstance(node, ast.Return):
            if node.value:
                save_to.write('    '*level)
                save_to.write('return')
                if not is_constant_none(node.value):
                    save_to.write(' ')
                    walk(node.value, save_to, level, lineno=lineno, col_offset=col_offset)
                else:
                    node.value.custom_ignore = True

                save_to.write(';\n')

        elif isinstance(node, ast.IfExp):
            target = ast.AnnAssign(
                target=ast.Name(id='success', ctx=ast.Store),
                annotation=ast.Name(id='unsigned int', ctx=ast.Load),
                value=None,
            )
            walk(target, save_to, level, lineno=lineno, col_offset=col_offset)

            save_to.write('    ' * level)
            save_to.write('if (')
            walk(node.test, save_to, lineno=lineno, col_offset=col_offset)
            save_to.write(') {\n')
            save_to.write('    ' * (level+1))
            # if for_ifexpr:
            #     walk(for_ifexpr, save_to)

            target = ast.Assign(
                targets=[ast.Name(id='success', ctx=ast.Store)],
                value=node.body,
            )
            walk(target, save_to, lineno=lineno, col_offset=col_offset)
            # save_to.write(';\n')
            save_to.write('    ' * level)
            save_to.write('} else {\n')
            save_to.write('    ' * (level+1))
            # if for_ifexpr:
            #     for_ifexpr.custom_ignore = False
            #     walk(for_ifexpr, save_to)

            target = ast.Assign(
                targets=[ast.Name(id='success', ctx=ast.Store)],
                value=node.orelse,
            )
            walk(target, save_to, lineno=lineno, col_offset=col_offset)
            # save_to.write(';\n')
            save_to.write('    ' * level)
            save_to.write('}\n\n')
            for_ifexpr['value'] = ast.Name(id='success', ctx=ast.Load)

        elif isinstance(node, ast.If):
            save_to.write('    '*level)
            save_to.write('if (')
            walk(node.test, save_to, level, lineno=lineno, col_offset=col_offset)
            save_to.write(') {\n')
            for node_body in node.body:
                walk(node_body, save_to, level+1, has_while_orelse, lineno=lineno, col_offset=col_offset)

            save_to.write('    '*level)
            save_to.write('}')
            if node.orelse:
                save_to.write(' else ')
                if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                    walk(node.orelse[0], save_to, level, has_while_orelse, lineno=lineno, col_offset=col_offset)
                else:
                    save_to.write('{\n')
                    for node_orelse in node.orelse:
                        walk(node_orelse, save_to, level+1, has_while_orelse, lineno=lineno, col_offset=col_offset)

                    save_to.write('    '*level)
                    save_to.write('}\n\n')
            else:
                save_to.write('\n\n')

        elif isinstance(node, ast.While):
            if node.orelse:
                save_to.write('    ' * level)
                save_to.write('unsigned byte success = 1;\n')

            save_to.write('    ' * level)
            save_to.write('while (')
            walk(node.test, save_to, level, lineno=lineno, col_offset=col_offset)
            save_to.write(') {\n')
            for node_body in node.body:
                # TODO: перед опретаором break необходимо выполнить код "success=0;".
                walk(node_body, save_to, level+1, has_while_orelse+[bool(node.orelse)], lineno=lineno, col_offset=col_offset)

            save_to.write('    '*level)
            save_to.write('}\n\n')
            if node.orelse:
                save_to.write('    ' * level)
                save_to.write('if (success == 1) {\n')
                walk(node.orelse[0], save_to, level+1, lineno=lineno, col_offset=col_offset)
                save_to.write('    ' * level)
                save_to.write('}\n\n')

        elif isinstance(node, ast.Break):
            if has_while_orelse[-1]:
                save_to.write('    ' * level)
                save_to.write('success = 0;\n')

            save_to.write('    ' * level)
            save_to.write('break;\n')

        elif isinstance(node, ast.Continue):
            save_to.write('    ' * level)
            save_to.write('continue;\n')

        elif isinstance(node, ast.Expr):
            save_to.write('    ' * level)
            walk(node.value, save_to, level, lineno=lineno, col_offset=col_offset)
            save_to.write(';\n')

        elif isinstance(node, (ast.Pass, ast.Module)):
            pass

        elif isinstance(node, ast.Import):
            for name in node.names:
                save_to.write(f'#include <{name.name}.h>\n')

            save_to.write('\n')

        elif isinstance(node, ast.ImportFrom):
            save_to.write(f'#include <{node.module}.h>\n')
            save_to.write('\n')

        elif isinstance(node, ast.Compare):
            walk(node.left, save_to, level, lineno=lineno, col_offset=col_offset)
            for op, right in zip(node.ops, node.comparators):
                save_to.write(' {} '.format(convert_compare_op(op)))
                walk(right, save_to, level, lineno=lineno, col_offset=col_offset)
        else:
            raise SourceCodeException(f'unknown node: {node.__class__.__name__} {str(parent_node)}', node)


def main(source_code, save_to):
    tree = ast.parse(source_code)
    walk(tree, save_to)


if __name__ == '__main__':
    import os

    with open('example/example.py') as example_py_file:
        source_code = example_py_file.read()

    with open('example.c', 'w') as example_c_file:
        main(source_code, save_to=example_c_file)

    path_example_from_book = 'example/from_book/'
    for filepath in os.listdir(path_example_from_book):
        print()
        print(filepath)
        with open(os.path.join(path_example_from_book, filepath)) as example_py_file:
            source_code = example_py_file.read()

        with open(f'{filepath}.c', 'w') as example_c_file:
            main(source_code, save_to=example_c_file)
