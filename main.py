"""
Поддерживаются следующие операции:
- присваивание переменным константных значений: целые положительные числа и строки.

Ограничения:
- типы всегда объявлять через аннотацию при инициализации.
- все целые положительные числа по умолчанию имеют c-тип "int"
- строки по умолчанию - тип "unsigned char"
- аннотация типов сработает, если она укахана перед присвоением. Если указана в мемоент или после присвоения, то аннотация прогнорируется


TODO:
 - указывать другой c-тип для целых типов, например "byte", "long"
"""

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

class OpMap:
    def __getattr__(self, key):
        return dis.opmap[key]


def guess_type(value):
    if isinstance(value, int):
        return 'unsigned int', str(value)
    elif isinstance(value, str):
        return 'char', '"{}"'.format(value)
    
    return 'unknown', str(value)


def guess_type_by_class(value):
    if value is int:
        return 'unsigned int'
    elif value is str:
        return 'char'
    
    return 'unknown'
    

opmap = OpMap()
buffer = []
annotations = {}
previous_instr = None
def main(source_code):
    for instr in dis.get_instructions(source_code):
        # print('  ', instr.opcode, instr.opname, instr.arg, instr.argval, instr.starts_line)
        print('  ', instr.opname.ljust(10), instr.argval)
        if instr.opcode == opmap.LOAD_CONST:
            instr.c_type, instr.c_view = guess_type(instr.argval)
            #instr.source_value = instr.argval
            buffer.append(instr)

        elif instr.opcode == opmap.LOAD_NAME:
            instr.c_type = annotations.get(instr.argval, 'unknown')
            instr.c_view = instr.argval
            buffer.append(instr)

        elif instr.opcode == opmap.STORE_NAME:
            if not buffer:  # clear afte MAKE_FUNCTION operator
                continue
                
            buf_instr = buffer.pop()
            #if buf_instr.c_type == 'char' and len(buf_instr.source_value) > 1:
            #    print('{} {}[{}] = "{}";'.format(buf_instr.c_type, instr.argval, len(buf_instr.source_value), buf_instr.source_value))
            #else:
            if instr.argval in annotations:
                  print('{} = {};'.format(instr.argval, buf_instr.c_view))
            instr.variable_value = buf_instr.argval
            
            previous_instr = instr
            
            #source_type = annotations.setdefault(instr.argval, buf_instr.c_type)
            #if source_type != buf_instr.c_type:
            #    print('TypeError: var "{}" has type "{}", but has got type "{}"'.format(instr.argval, source_type, buf_instr.c_type))
            #    print('Line is', buf_instr.starts_line)
            #    exit()

        elif instr.opcode == opmap.STORE_SUBSCR:
        
            buf_instr_key = buffer.pop()
            name = buffer.pop().argval
            buf_instr_value = buffer.pop()

            if name == '__annotations__':
                instr_var = buf_instr_key
                instr_type = buf_instr_value
                if previous_instr and previous_instr.opcode == opmap.STORE_NAME:
                    if instr_var.argval == previous_instr.argval:
                        var_value = previous_instr.variable_value
                        check_type = c_types.get(instr_type.argval)
                        if not check_type:
                            print('Unknown type: {}'.format(instr_type.argval))
                            exit()
                            
                        if not (var_value is None or check_type(var_value)):
                            print('Unmatched type {} for value {}'.format(instr_type.argval, var_value))
                            exit()
                            
                        if var_value is None:
                            print('{} {};'.format(instr_type.argval, instr_var.argval))
                        else:
                            print('{} {} = {};'.format(instr_type.argval, instr_var.argval, var_value))
                    else:
                        print('{} {};'.format(instr_type.argval, instr_var.argval))
                else:
                    print('{} {};'.format(instr_type.argval, instr_var.argval))
                    
                annotations[instr_var.argval] = instr_type.argval
                #if buf_instr_key.argval not in annotations:
                #    c_type = guess_type_by_class(getattr(__builtins__, buf_instr_value.argval))
                #    print('{} {};'.format(c_type, buf_instr_key.argval))
            else:
                print('{}[{}] = {};'.format(name, buf_instr_key.argval, buf_instr_.argval))

        elif instr.opcode == opmap.MAKE_FUNCTION:
            instr_funcname = buffer.pop()
            instr_funcobj = buffer.pop()
            
            print('{}() {{}};'.format(instr_funcname.argval))

        elif instr.opcode == opmap.BUILD_CONST_KEY_MAP:
            
            buffer.pop() # deleting ('return',) here
            c_type_name = buffer.pop().argval
            func_name = buffer.pop().argval
            
            annotations[func_name] = c_type_name
        
        # Binary operations

        elif instr.opcode == opmap.BINARY_ADD:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
            
            if arg2.c_type != arg1.c_type:
                print('Types are not equal for binary operation! ({} and {})'.format(arg2.c_type, arg1.c_type))
                exit()
               
            arg1.c_view = '({} + {})'.format(arg1.c_view, arg2.c_view)

        elif instr.opcode == opmap.BINARY_SUBTRACT:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
            
            if arg2.c_type != arg1.c_type:
                print('Types are not equal for binary operation! ({} and {})'.format(arg2.c_type, arg1.c_type))
                exit()
               
            arg1.c_view = '({} - {})'.format(arg1.c_view, arg2.c_view)
            
        elif instr.opcode == opmap.BINARY_TRUE_DIVIDE:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
            
            if arg2.c_type != arg1.c_type:
                print('Types are not equal for binary operation! ({} and {})'.format(arg2.c_type, arg1.c_type))
                exit()
               
            arg1.c_view = '({} / {})'.format(arg1.c_view, arg2.c_view)

        elif instr.opcode == opmap.BINARY_MULTIPLY:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
            
            if arg2.c_type != arg1.c_type:
                print('Types are not equal for binary operation! ({} and {})'.format(arg2.c_type, arg1.c_type))
                exit()
               
            arg1.c_view = '({} * {})'.format(arg1.c_view, arg2.c_view)

        elif instr.opcode == opmap.BINARY_LSHIFT:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
            
            if arg2.c_type != arg1.c_type:
                print('Types are not equal for binary operation! ({} and {})'.format(arg2.c_type, arg1.c_type))
                exit()
               
            arg1.c_view = '({} << {})'.format(arg1.c_view, arg2.c_view)

        elif instr.opcode == opmap.BINARY_RSHIFT:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
            
            if arg2.c_type != arg1.c_type:
                print('Types are not equal for binary operation! ({} and {})'.format(arg2.c_type, arg1.c_type))
                exit()
               
            arg1.c_view = '({} >> {})'.format(arg1.c_view, arg2.c_view)
            
        elif instr.opcode == opmap.BINARY_AND:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
            
            if arg2.c_type != arg1.c_type:
                print('Types are not equal for binary operation! ({} and {})'.format(arg2.c_type, arg1.c_type))
                exit()
               
            arg1.c_view = '({} & {})'.format(arg1.c_view, arg2.c_view)

        elif instr.opcode == opmap.BINARY_XOR:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
            
            if arg2.c_type != arg1.c_type:
                print('Types are not equal for binary operation! ({} and {})'.format(arg2.c_type, arg1.c_type))
                exit()
               
            arg1.c_view = '({} ^ {})'.format(arg1.c_view, arg2.c_view)

        elif instr.opcode == opmap.BINARY_OR:
        
            arg2 = buffer.pop()
            arg1 = buffer[-1]
            
            if arg2.c_type != arg1.c_type:
                print('Types are not equal for binary operation! ({} and {})'.format(arg2.c_type, arg1.c_type))
                exit()
               
            arg1.c_view = '({} | {})'.format(arg1.c_view, arg2.c_view)

        elif instr.opcode == opmap.SETUP_ANNOTATIONS:
            continue
        else:
            print('Unknown opname: {} {}'.format(instr.opcode, instr.opname))

        #elif instr.opcode == opmap.BINARY_MODULO: # TODO: '%'
        #elif instr.opcode == opmap.BINARY_FLOOR_DIVIDE: # TODO: '//'
        #elif instr.opcode == opmap.BINARY_MATRIX_MULTIPLY: # TODO: '@'
        #elif instr.opcode == opmap.BINARY_POWER: # TODO: '**'
        #elif instr.opcode == opmap.BINARY_SUBSCR: # TODO: 'TOS = TOS1[TOS]'
        #elif instr.opcode == opmap.BINARY_MODULO: # TODO: '%'
        #elif instr.opcode == opmap.BINARY_MODULO: # TODO: '%'
        #elif instr.opcode == opmap.BINARY_MODULO: # TODO: '%'
        #elif instr.opcode == opmap.BINARY_MODULO: # TODO: '%'
        #elif instr.opcode == opmap.BINARY_MODULO: # TODO: '%'
        #elif instr.opcode == opmap.BINARY_MODULO: # TODO: '%'


if __name__ == '__main__':
    source_code = """
var1: 'unsigned int' = 10    # unsigned int var1 = 10;
var2: 'unsigned int' = None  # unsigned int var2;
var3: 'unsigned int'         # unsigned int var3;
var4: 'unsigned char' = 'a'
var5: 'unsigned char' = 20

def func1() -> 'void': # void func1() {};
    return None

def func2() -> 'unsigned char': # unsigned char func2() {};
    return 'c'

def func3() -> 'unsigned char':
    return 'c', 6

var5 = func2()

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
cbf2 = cbf or 34
cd = 'g'
cd = 6
"""
    main(source_code)
