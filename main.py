import dis


def check_type_char(value):
    return isinstance(value, int) and -128 <= value <= 127


def check_type_unsigned_char(value):
    return (isinstance(value, int) and 0 <= value <= 255) or (isinstance(value, str) and len(value) == 1 and bytes(value, 'ascii')[0] <= 255)


def check_type_int(value):
    return isinstance(value, int) and -32768 <= value <= 32767


def check_type_unsigned_int(value):
    return isinstance(value, int) and 0 <= value <= 65535


def check_type_long_int(value):
    return isinstance(value, int) and 0 <= value <= 0


def check_type_void(value):
    return value is None


c_types = {
    'char': check_type_char,
    'unsigned char': check_type_unsigned_char,
    'int': check_type_int,
    'unsigned int': check_type_unsigned_int,
    'void': check_type_void,
}

def is_variable_exists(variable_name):
    ctype = annotations.get(variable_name)
    if not ctype:
        print('Variable {} does not exists'.format(variable_name))
        exit()
    
    return ctype

def is_value_matched_type(value, ctype):
    checking_function = c_types.get(ctype)
    if not checking_function:
        print('Unknown type: {}'.format(ctype))
        exit()
    
    if value is not None and not checking_function(value):
        print('Unmatched type "{}" for value "{}"'.format(ctype, value))
        exit()

def are_types_matched(ctype1, ctype2):
    if ctype1 != ctype2:
        #print('Unmatched type "{}" for variable "{}"'.format(type1, variable_name))
        print('Unmatched types: "{}" and "{}"'.format(ctype1, ctype2))
        exit()



class OpMap:
    def __getattr__(self, key):
        return dis.opmap[key]


opmap = OpMap()
BINARY_OPERATIONS = {
    opmap.BINARY_OR: '{} | {}',
    opmap.BINARY_XOR: '{} ^ {}',
    opmap.BINARY_AND: '{} & {}',
    opmap.BINARY_RSHIFT: '{} >> {}',
    opmap.BINARY_LSHIFT: '{} << {}',
    opmap.BINARY_MULTIPLY: '{} * {}',
    opmap.BINARY_TRUE_DIVIDE: '{} / {}',
    opmap.BINARY_SUBTRACT: '{} - {}',
    opmap.BINARY_ADD: '{} + {}',
}
buffer = []
annotations = {}
previous_instr = None
functions = {}

def get_c_view_value(value):
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        return '"{}"'.format(value)


def get_c_view_name(name):    
    return name


'''def get_c_view(instr):
    if hasattr(instr, 'c_view'):
        return instr.c_view

    if instr.opcode == opmap.LOAD_CONST:
        return get_c_view_value(instr.argval)
    elif instr.opcode == opmap.LOAD_NAME:
        return get_c_view_name(instr.argval)
    #elif instr.opcode == opmap.CALL_FUNCTION:
    #    return '{}()'.format(instr.argval)
            
    print('unknown python-type')
    exit()
'''

class Stack:
    ident_level = 0
    
    def __init__(self, ident_level):
        self.ident_level = ident_level
    
    def print_c_code(self, line, *args):
        print('  '*self.ident_level, line.format(*args), sep='')

        
def main(source_code, ident_level=0, call_level=0):
    stack = Stack(ident_level)
    for index, instr in enumerate(dis.get_instructions(source_code)):
        # print('  ', instr.opcode, instr.opname, instr.arg, instr.argval, instr.starts_line)
        print('  ', index, instr.opname.ljust(10), instr.argval)
        if instr.opcode == opmap.LOAD_CONST:

            instr.c_view = get_c_view_value(instr.argval)
            buffer.append(instr)

        elif instr.opcode == opmap.LOAD_NAME: 
        
            instr.c_view = get_c_view_name(instr.argval)
            buffer.append(instr)

        elif instr.opcode in (opmap.STORE_NAME, opmap.STORE_FAST):
            
            if not buffer:  # it's clear after MAKE_FUNCTION operator
                continue
                
            buf_instr = buffer.pop()
            if instr.argval in annotations:  # if variable exists and we do assigning
                stack.print_c_code('{} = {};', instr.argval, buf_instr.c_view)

            instr.variable_value = buf_instr.argval
            instr.c_view = buf_instr.c_view
            instr.variable_opcode = buf_instr.opcode
            previous_instr = instr

        elif instr.opcode == opmap.STORE_SUBSCR:
        
            buf_instr_key = buffer.pop()
            name = buffer.pop().argval
            buf_instr_value = buffer.pop()

            if name == '__annotations__':
                variable_ctype = buf_instr_value.argval
                variable_name = buf_instr_key.argval
                if previous_instr:
                    if variable_name == previous_instr.argval:
                        variable_value = previous_instr.variable_value
                        if previous_instr.variable_opcode == opmap.LOAD_CONST:
                            is_value_matched_type(variable_value, variable_ctype)
                            
                        if variable_value is None:
                            stack.print_c_code('{} {};', variable_ctype, variable_name)
                        else:
                            stack.print_c_code('{} {} = {};', variable_ctype, variable_name, previous_instr.c_view)
                    else:
                        stack.print_c_code('{} {};', variable_ctype, variable_name)
                else:  # if the variable was created without value
                    stack.print_c_code('{} {};', variable_ctype, variable_name)
                
                previous_instr = None
                annotations[variable_name] = variable_ctype
            else:
                stack.print_c_code('{}[{}] = {};', name, buf_instr_key.argval, buf_instr_.argval)

        elif instr.opcode == opmap.MAKE_FUNCTION:
            
            func_name = buffer.pop().argval
            func_obj = buffer.pop().argval
            function = buffer.pop()
            
            func_annotation = function['annotations'].get('return')  # TODO: если у функции нет аннотации, то по умолчанию - "void"
            if not func_annotation:
                print('Function "{}" has no annotation!'.format(func_name))
                exit()

            annotations[func_name] = func_annotation
            args = ['{} {}'.format(arg_c_type, arg_name) for arg_name, arg_c_type in function['annotations'].items() if arg_name != 'return']
            stack.print_c_code('{} {}({}) {{', func_annotation, func_name, ', '.join(args))
            main(func_obj, ident_level+1, call_level+1)
            stack.print_c_code('}};')

        elif instr.opcode == opmap.BUILD_CONST_KEY_MAP:
        
            function = {'annotations': {}, 'default': None}
            
            arg_names = list(buffer.pop().argval)
            arg_names.reverse()
            for arg_name in arg_names:
                function['annotations'][arg_name] = buffer.pop().argval

            function['default'] = buffer.pop().argval if buffer else tuple()
            buffer.append(function)

        elif instr.opcode == opmap.RETURN_VALUE:
                    
            buff_instr = buffer.pop()
            if call_level > 0:
                if buff_instr.argval is not None:
                    stack.print_c_code('return {};', buff_instr.c_view)
                else:
                    stack.print_c_code('return;')

        elif instr.opcode in BINARY_OPERATIONS:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
                
            val1 = arg1.argval
            val2 = arg2.argval
           
            is_matched = True
            c_type = None
            value = None
            if arg1.opcode == opmap.LOAD_CONST and arg2.opcode == opmap.LOAD_CONST:
                is_matched = val1 is int and val2 is int
                value = val1
            elif arg1.opcode == opmap.LOAD_NAME and arg2.opcode == opmap.LOAD_NAME:
                c_type = is_variable_exists(val1)
                c_type2 = is_variable_exists(val2)
                are_types_matched(c_type, c_type2)
            else:
                any_value = arg1.argval if arg1.opcode == opmap.LOAD_CONST else arg2.argval
                any_name = arg1.argval if arg1.opcode == opmap.LOAD_NAME else arg2.argval
                c_type = is_variable_exists(any_name)
                is_value_matched_type(any_value, c_type)
                
            if not is_matched:         
                 print('Types are not compatible for value: "{}" and "{}"'.format(val1, val2))
                 exit()
                
            c_view = BINARY_OPERATIONS[instr.opcode]
            arg1.c_view = c_view.format(arg1.c_view, arg2.c_view)
            arg1.c_view = '({})'.format(arg1.c_view)
            arg1.value = value

        elif instr.opcode == opmap.CALL_FUNCTION:
            
            buff_instr = buffer[-1]
            buff_instr.c_view = '{}()'.format(buff_instr.c_view)

        elif instr.opcode == opmap.COMPARE_OP:

            instr_arg1 = buffer.pop()
            instr_arg2 = buffer[-1]
            
            c_view1 = instr_arg1.c_view
            c_view2 = instr_arg2.c_view
            
            c_view_compare = '{} {} {}'.format(c_view2, instr.argval, c_view1)
            instr_arg2.c_view = c_view_compare            
            #print(c_view_compare)

        elif instr.opcode == opmap.POP_JUMP_IF_FALSE:
        
            buff_instr = buffer.pop()
            
            stack.print_c_code('if ({}) {{', buff_instr.c_view)
            stack.ident_level += 1
            #print_c_code('}};')

        elif instr.opcode == opmap.SETUP_ANNOTATIONS:
            continue
        else:
            print('Unknown opname: {} {}'.format(instr.opcode, instr.opname))

        #elif instr.opcode == opmap.BINARY_MODULO: # TODO: '%'
        #elif instr.opcode == opmap.BINARY_FLOOR_DIVIDE: # TODO: '//'
        #elif instr.opcode == opmap.BINARY_MATRIX_MULTIPLY: # TODO: '@'
        #elif instr.opcode == opmap.BINARY_POWER: # TODO: '**'
        #elif instr.opcode == opmap.BINARY_SUBSCR: # TODO: 'TOS = TOS1[TOS]'


if __name__ == '__main__':
    source_code = """
var1: 'unsigned int' = 10    # unsigned int var1 = 10;
var2: 'unsigned int' = None  # unsigned int var2;
var3: 'unsigned int'         # unsigned int var3;
var4: 'unsigned char' = 'a'
var5: 'unsigned char' = 20

def func1() -> 'void': # void func1() {};
    return None

def func2(arg1, arg2: 'ct1'=5, arg3: 'ct2'=8, arg4 = 10) -> 'unsigned char': # unsigned char func2() {};
    return 'c'

def func3() -> 'unsigned char':
    fvar: 'unsigned int' = 78
    return 'c', 6

var5 = func2() + 67 + var4

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
"""
    main(source_code)
