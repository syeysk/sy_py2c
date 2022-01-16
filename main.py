"""
Поддерживаются следующие операции:
- присваивание переменным константных значений: целые положительные числа и строки.

Ограничения:
- все целые положительные числа по умолчанию имеют c-тип "unsigned int"
- аннотация типов сработает, если она укахана перед присвоением. Если указана в мемоент или после присвоения, то аннотация прогнорируется


TODO:
 - указывать другой c-тип для целых типов, например "byte", "long"
"""

import dis

source_code = """
a = 10
b: int = 25
novalue: int
yesvalue: int = a
cbf = 10
cbf2 = cbf * (24 + a)
cbf2 = cbf * 24 + a
cbf2 = 24 + a * cbf
cbf2 = cbf - 34
cbf2 = cbf * 34
cbf2 = cbf / 34
cbf2 = cbf | 34
cbf2 = cbf or 34
cd = 'ghj'
cd = 6
"""

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
        buf_instr = buffer.pop()
        #if buf_instr.c_type == 'char' and len(buf_instr.source_value) > 1:
        #    print('{} {}[{}] = "{}";'.format(buf_instr.c_type, instr.argval, len(buf_instr.source_value), buf_instr.source_value))
        #else:
        print('{} {} = {};'.format(buf_instr.c_type, instr.argval, buf_instr.c_view))
        
        source_type = annotations.setdefault(instr.argval, buf_instr.c_type)
        if source_type != buf_instr.c_type:
            print('TypeError: var "{}" has type "{}", but has got type "{}"'.format(instr.argval, source_type, buf_instr.c_type))
            print('Line is', buf_instr.starts_line)
            exit()

    elif instr.opcode == opmap.STORE_SUBSCR:
    
        buffer_instr_key = buffer.pop()
        name = buffer.pop().argval
        buffer_instr_value = buffer.pop()

        if name == '__annotations__':
            if buffer_instr_key.argval not in annotations:
                c_type = guess_type_by_class(getattr(__builtins__, buffer_instr_value.argval))
                print('{} {};'.format(c_type, buffer_instr_key.argval))
                annotations[buffer_instr_key.argval] = c_type
        else:
            print('{}[{}] = {};'.format(name, buffer_instr_key.argval, buffer_instr_.argval))

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
