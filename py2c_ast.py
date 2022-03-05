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


def walk(parent_node, save_to, level=0):    
    if parent_node is None:
        save_to.write('None')
        return

    for node in chain([parent_node], ast.iter_child_nodes(parent_node)):
        if hasattr(node, 'custom_ignore'):
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
            save_to.write('    '*level)
            for target in node.targets:
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
            
            save_to.write(', '.join(str_args))
            save_to.write(') {\n')
            for node_body in node.body:
                walk(node_body, save_to, level+1)
                
            save_to.write('}\n')
        elif isinstance(node, ast.Call):
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
                save_to.write('NULL') # для указателей
            elif isinstance(value, str):
                save_to.write('"{}"'.format(node.value))
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
        elif isinstance(node, ast.If):
            save_to.write('    '*level)
            save_to.write('if (')
            walk(node.test, save_to, level)
            save_to.write(') {\n')
            for node_body in node.body:
                walk(node_body, save_to, level+1)
   
            save_to.write('    '*level)
            save_to.write('}')
            if node.orelse:
                save_to.write(' else ')
                if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                    walk(node.orelse[0], save_to, level)
                else:
                    save_to.write('{\n' )
                    for node_orelse in node.orelse:
                        walk(node_orelse, save_to, level+1)
   
                    save_to.write('    '*level)
                    save_to.write('}\n\n')
            else:
                save_to.write('\n\n')
            
        elif isinstance(node, ast.Compare):
            walk(node.left, save_to, level)
            for op, right in zip(node.ops, node.comparators):
                save_to.write(' {} '.format(convert_compare_op(op)))
                walk(right, save_to, level)    
        else:
            print('    '*level, node, 'unknown node')


def main(source_code, save_to=print):
    tree = ast.parse(source_code)
    walk(tree, save_to)


if __name__ == '__main__':
    source_code = """
var1: 'unsigned int' = 10    # unsigned int var1 = 10;
var2: 'unsigned int' = None  # unsigned int var2;
var3: 'unsigned int'         # unsigned int var3;
var4: 'unsigned char' = 'a'
var5: 'unsigned char' = 20

def func1() -> 'void': # void func1() {};
    return None

def func2(arg1: 'ann1', arg2: 'ct1'=5, arg3: 'ct2'=8, arg4: 'ann2' = 10) -> 'unsigned char': # unsigned char func2() {};
    return 'c'

def func3() -> 'unsigned char':
    fvar: 'unsigned int2' = 78
    if fvar > 9:
        return 56
    elif fvar < 5:
        return 67
        
    if fvar > 9:
        fvar = 56
    elif fvar > 5:
        fvar = 67
    elif fvar > 1:
        fvar = 90
    else:
        fvar = 0
        
    if fvar > 9:
        fvar = 56
    else:
        fvar = 67
        fvar += 5

    return 'c', 6

var5 = func2(var5, 897) + 67 + var4

#a = 10
#b: int = 25
#novalue: int
#yesvalue: int = a
cbf: 'unsigned int' = 10
cbf2: 'unsigned int' = cbf * (24 + var1) # TODO: проверять все операнды на соответствие типа
cbf2 = cbf * 24 + var1
cbf2 = 24 + var1 * cbf
cbf2 = cbf - 34
cbf2 = cbf * 34
cbf2 = cbf / 34
cbf2 = cbf | 34
cbf2 = cbf or 34  # нужен ли данный код?
cd = 'g'
cd = 6
ab: 'unsigned int' = cd == 7  # бесполезный код. Если такая переменная используется в условии, то её следует заменить на смао выражение
if cd == 7:
    cbf = 15
    
cd += 1
cd -= 1
cd = -cd
"""

    with open('example.c', 'w') as example_c_file:
        main(source_code, save_to=example_c_file)
