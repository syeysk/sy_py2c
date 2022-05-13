# tool_py2c_translator

Translator Python source into C.

Поддерживаются следующие операции:
- присваивание переменным константных значений: целые положительные числа и строки.

Ограничения:
- типы всегда объявлять через аннотацию при инициализации.
- аннотация типов сработает, если она указана перед присвоением. Если указана в момент или после присвоения, то аннотация прогнорируется
- все аргументы - обязательны (в планах - добавить возможность указывать аргументы по умолчанию)
- функция всегда возвращает только одно значение (в планах - сделать возврат массива для возврата нескольких значений)

- все целые положительные числа по умолчанию имеют c-тип "int"
- строки по умолчанию - тип "unsigned char"

# ROADMAP

## Add dataset for:
- [ ] initing difficult vars: generative lists, dicts, multi-ifs
- [ ] initing vars with dict (structure in C), list (arrays in C), tupple and set.
- [ ] conditions and cycles: if-elif-else, while-else, for, switch
- [ ] functions: without args and return, with args and one return, with multi-return, with default args.
- [ ] imports and standart c-library
- [ ] c-pointers
- [ ] collecting vars and placing their initing into start of program/function
- [ ] using constants - all uppercase vars will be recognise like c-constant: `VARIABLE = 67` -> `const variable = 67;` or `#def VARIABLE 67`

## Other

- [ ] Write tests for datasets
- [ ] Realise supporting all code in dataset
- [ ] Add online-compilation by GCC on server
- [ ] Add modules for calculating registers of microcontrollers (AVR, STM8). It will be a class with some properties: cpu-frequrence, settings of i2c, input/output and other
- [ ] Set package manager (poetry)
- [ ] Set allowed modules for import: math, microcontrollers.

## Add dataset with mistake code:

- [ ] vars without annotations
- [ ] trying to changing annotation or assigning value with another type


## Tests
- [ ] tests of variables and operators
- [ ] tests of constructions
- [ ] tests of functions
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