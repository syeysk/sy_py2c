import ast
from itertools import chain


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
        print(node, 'unknown node operator')


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
        print(node, 'unknown node compare operator')


def convert_bool_op(node):
    node.custom_ignore = True
    if isinstance(node, ast.Or):
        return '||'
    elif isinstance(node, ast.And):
        return '&&'
    else:
        print(node, 'unknown node bool operator')


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
        print(node, 'unknown node unary operator')


def is_constant_none(node):
    return isinstance(node, ast.Constant) and node.value is None


def convert_annotation(node):
    if node is None:
        print('annotation must be!')
        exit()
        
    node.custom_ignore = True        
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant):
        return node.value
    
    print(node, 'unknown annotation node')
    exit()


def walk(parent_node, save_to, level=0, has_while_orelse=None, for_ifexpr=None):
    if parent_node is None:
        save_to.write('None')
        return

    if has_while_orelse is None:
        has_while_orelse = []

    for node in chain([parent_node], ast.iter_child_nodes(parent_node)):
        if hasattr(node, 'custom_ignore') and node.custom_ignore:
            continue
            
        node.custom_ignore = True
        if isinstance(node, ast.AnnAssign):
            save_to.write('    '*level)
            ann_name = convert_annotation(node.annotation)
            save_to.write(f'{ann_name} ')
            walk(node.target, save_to, level)
            if node.value and not is_constant_none(node):
                save_to.write(' = ')
                walk(node.value, save_to, level)

            save_to.write(';\n')

        elif isinstance(node, ast.Assign):
            if isinstance(node.value, ast.IfExp):
                data = {'target': node.targets[0], 'value': None}
                walk(node.value, save_to, level, for_ifexpr=data)
                data['target'].custom_ignore = False
                node.value = data['value']

            for target in node.targets:
                save_to.write('    ' * level)
                walk(target, save_to, level)
                save_to.write(' = ')
                walk(node.value, save_to, level)
                save_to.write(';\n')

        elif isinstance(node, ast.AugAssign):
            save_to.write('    '*level)
            walk(node.target, save_to, level)
            save_to.write(' {}= '.format(convert_op(node.op)))
            walk(node.value, save_to, level)
            save_to.write(';\n')

        elif isinstance(node, ast.FunctionDef):
            save_to.write('    '*level)
            ann_name = convert_annotation(node.returns)
            save_to.write(f'{ann_name} {node.name}(')
            str_args = []
            data_args = node.args
            for arg in data_args.args:
                ann_name = convert_annotation(arg.annotation)
                str_args.append(f'{ann_name} {arg.arg}')
            
            save_to.write(', '.join(str_args) if data_args.args else 'void')
            save_to.write(') {\n')
            for node_body in node.body:
                walk(node_body, save_to, level+1)
                
            save_to.write('}\n')

        elif isinstance(node, ast.Call):  # TODO: обрабатывать другие виды аргуентов
            walk(node.func, save_to, level)
            save_to.write(f'(')
            for arg in node.args:
                walk(arg, save_to, level)
                save_to.write(', ')
            
            for keyword in node.keywords:
                #walk(arg, save_to, level)
                save_to.write(', ')
            
            save_to.write(')')

        elif isinstance(node, ast.Constant):
            value = node.value
            if value is None:
                save_to.write('NULL')  # для указателей
            elif isinstance(value, str):
                save_to.write('"{}"'.format(node.value))
            elif isinstance(value, bool):
                save_to.write('{}'.format(1 if node.value else 0))
            elif isinstance(value, (int, float)):
                save_to.write('{}'.format(node.value))

        elif isinstance(node, ast.Name):
            save_to.write('{}'.format(node.id))

        elif isinstance(node, ast.BinOp):
            walk(node.left, save_to, level)
            save_to.write(' {} '.format(convert_op(node.op)))
            walk(node.right, save_to, level)

        elif isinstance(node, ast.BoolOp):
            walk(node.values[0], save_to, level)
            for value in node.values[1:]:
                save_to.write(' {} '.format(convert_bool_op(node.op)))
                walk(value, save_to, level)

        elif isinstance(node, ast.UnaryOp):
                save_to.write(' {}'.format(convert_unary_op(node.op)))
                walk(node.operand, save_to, level)

        elif isinstance(node, ast.Return):
            if node.value:
                save_to.write('    '*level)
                save_to.write('return')
                if not is_constant_none(node.value):
                    save_to.write(' ')
                    walk(node.value, save_to, level)
                else:
                    node.value.custom_ignore = True

                save_to.write(';\n')

        elif isinstance(node, ast.IfExp):
            target = ast.AnnAssign(
                target=ast.Name(id='success', ctx=ast.Store),
                annotation=ast.Name(id='unsigned int', ctx=ast.Load),
                value=None,
            )
            walk(target, save_to, level)

            save_to.write('    ' * level)
            save_to.write('if (')
            walk(node.test, save_to)
            save_to.write(') {\n')
            save_to.write('    ' * (level+1))
            # if for_ifexpr:
            #     walk(for_ifexpr, save_to)

            target = ast.Assign(
                targets=[ast.Name(id='success', ctx=ast.Store)],
                value=node.body,
            )
            walk(target, save_to)
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
            walk(target, save_to)
            # save_to.write(';\n')
            save_to.write('    ' * level)
            save_to.write('}\n\n')
            for_ifexpr['value'] = ast.Name(id='success', ctx=ast.Load)

        elif isinstance(node, ast.If):
            save_to.write('    '*level)
            save_to.write('if (')
            walk(node.test, save_to, level)
            save_to.write(') {\n')
            for node_body in node.body:
                walk(node_body, save_to, level+1, has_while_orelse)
   
            save_to.write('    '*level)
            save_to.write('}')
            if node.orelse:
                save_to.write(' else ')
                if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                    walk(node.orelse[0], save_to, level, has_while_orelse)
                else:
                    save_to.write('{\n')
                    for node_orelse in node.orelse:
                        walk(node_orelse, save_to, level+1, has_while_orelse)
   
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
            walk(node.test, save_to, level)
            save_to.write(') {\n')
            for node_body in node.body:
                # TODO: перед опретаором break необходимо выполнить код "success=0;".
                walk(node_body, save_to, level+1, has_while_orelse+[bool(node.orelse)])

            save_to.write('    '*level)
            save_to.write('}\n\n')
            if node.orelse:
                save_to.write('    ' * level)
                save_to.write('if (success == 1) {\n')
                walk(node.orelse[0], save_to, level+1)
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
            walk(node.value, save_to, level)
            save_to.write(';\n')

        elif isinstance(node, ast.Pass):
            pass

        elif isinstance(node, ast.Import):
            for name in node.names:
                save_to.write(f'#include <{name.name}.h>\n')

            save_to.write('\n')

        elif isinstance(node, ast.ImportFrom):
            save_to.write(f'#include <{node.module}.h>\n')
            save_to.write('\n')

        elif isinstance(node, ast.Compare):
            walk(node.left, save_to, level)
            for op, right in zip(node.ops, node.comparators):
                save_to.write(' {} '.format(convert_compare_op(op)))
                walk(right, save_to, level)    
        else:
            print('    '*level, node, 'unknown node')


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
