# tool_py2c_translator
Translator Python source into C.

Поддерживаются следующие операции:
- присваивание переменным константных значений: целые положительные числа и строки.

Ограничения:
- типы всегда объявлять через аннотацию при инициализации.
- аннотация типов сработает, если она указана перед присвоением. Если указана в момент или после присвоения, то аннотация прогнорируется
- все аргументы - обязательны (в планах - добавить возможность указывать аргументы по умолчанию)

- все целые положительные числа по умолчанию имеют c-тип "int"
- строки по умолчанию - тип "unsigned char"
