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

Not yet

## Links

- description of nodes: https://greentreesnakes.readthedocs.io/en/latest/nodes.html