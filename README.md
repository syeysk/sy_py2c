# Translator from Python into C 

## Examples

Using is really simple with shortcuts:

```python
from py2c.shortcuts import trans_c

my_python_code = '''
    def hello(a: int, b: int = 5) -> string:
        return 'good' if a + b > 0 else 'not good'
'''

c_code = trans_c(my_python_code)
print(c_code)
```

Without shortcuts if you want more control:

```python
from py2c.bytecode_walker import translate
from py2c.translator_cpp import TranslatorC

my_python_code = '''
    def hello(a: int, b: int = 5) -> string:
        return 'good' if a + b > 0 else 'not good'
'''

with open('c_code.c') as c_file:
    translator = TranslatorC(save_to=c_file)
    translate(translator, my_python_code)
```

## Methods' description

`py2c.shortcuts.trans_c(source_code, write_to=None)`:
- `source_code` - a source python-code like unicode string (type of `str`) or text file object (returning `open` function)
- `write_to` - file object to write a result c-code. If `write_to` is `None` (as default), the function will return the c-code as string (type of `str`)

## Install

```bash
pip install git+https://github.com/syeysk/tool_py2c_translator.git
```

Поддерживаются следующие операции:
- присваивание переменным константных значений: целые положительные числа и строки.

Ограничения:
- типы всегда объявлять через аннотацию при инициализации.
- аннотация типов сработает, если она указана перед присвоением. Если указана в момент или после присвоения, то аннотация прогнорируется
- функция всегда возвращает только одно значение (в планах - сделать возврат массива для возврата нескольких значений)

- все целые положительные числа по умолчанию имеют c-тип "int"
- строки по умолчанию - тип "unsigned char"

# ROADMAP

## Add dataset for:
- [ ] initing difficult vars: generative lists, dicts
- [ ] initing vars with dict (structure in C), list (arrays in C), tupple and set.
- [ ] conditions and cycles: for, switch
- [ ] functions: with multi-return.
- [ ] c-pointers
- [ ] collecting vars and placing their initing into start of program/function

## Other

- [ ] Add online-compilation by GCC on server
- [ ] Add modules for calculating registers of microcontrollers (AVR, STM8). It will be a class with some properties: cpu-frequrence, settings of i2c, input/output and other
- [ ] Set package manager (poetry)
- [ ] Set allowed modules for import: math, microcontrollers.
- [ ] Arithmetic priory
- [ ] Brackets

## Tests
- [ ] tests of simple programs with different features

## Standarts of C

About standarts:
- http://www.open-std.org/jtc1/sc22/wg14/
- 

- [ ] K&R C
- [ ] C89
- [ ] C90
- [ ] C95
- [ ] C99
- [ ] C11
- [ ] C17
- [ ] C2x

## Versions of Python

- 3.6
- 3.8

## Links

- description of nodes: https://greentreesnakes.readthedocs.io/en/latest/nodes.html