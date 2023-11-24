# Транслятор из Python в C ([english version](README.md))

Используйте синтаксис Python, чтобы писать чистый C-код для ваших микроконтроллеров:

![](docs/this-py2c-translator.png)

## Примеры

Используйте короткую функцию для простоты:

```python
from py2c.shortcuts import trans_c

my_python_code = '''
    def hello(a: int, b: int = 5) -> string:
        return 'good' if a + b > 0 else 'not good'
'''

c_code = trans_c(my_python_code)
print(c_code)
```

Без короткой функции у вас больше контроля:

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

## Установка/Удаление

Используйте эту команду для установки Py2C:
```bash
pip install git+https://github.com/syeysk/tool_py2c_translator.git
```

Используйте эту команду для удаления Py2C:
```bash
pip uninstall py2c
```


## Описание функций и классов

`py2c.shortcuts.trans_c(source_code, write_to=None)` - транслирует python-код в c-код. Аргументы:
- `source_code` - исходный python-код в виде unicode-строки (типа `str`) или объект текстового файла (возвращаемый функцией `open`)
- `write_to` - файловый объект, в который будет записан результирующий c-код. Если `write_to` равен `None` (по умолчанию), то функция вернёт c-код как строку (типа `str`)

`py2c.TranslatorC(save_to)` - класс транслятора python-to-c. Содержит некоторые методы для трансляции конструкций. Аргументы:
- `save_to` - файловый объект, в который будет записан результирующий c-код

`py2c.translate(translator, source_code: str)` - конвертирует `source_code` в AST, обходит его и строит c-код. Arguments:
- `translator` - экземпляр транслятора. Например, `py2c.TranslatorC` или `py2c.TranslatorCpp`
- `source_code` - исходный python-код (типа `str`)

## Примеры интерфейса командной строки

Вы можете использовать `py2c` или `python -m py2c` равнозначно.

Создаёт *your_source_code.c* с c-кодом:
```bash
py2c your_source_code.py
```

Создаёт *your_output_code.c* с c-кодом:
```bash
py2c your_source_code.py -o your_output_code.c
```

Выводит c-код в консоль:
```bash
py2c your_source_code.py -p
```


## Trash :-D

Поддерживаются следующие операции:
- присваивание переменным константных значений: целые положительные числа и строки.

Ограничения:
- типы всегда объявлять через аннотацию при инициализации.
- функция всегда возвращает только одно значение (в планах - сделать возврат массива для возврата нескольких значений)

- все целые положительные числа по умолчанию имеют c-тип "int"
- строки по умолчанию - тип "unsigned char"

## Дорожная карта

[Дорожная карта](ROADMAP.ru.md)

## Поддержка

Если вам нужно помощь по Py2C, просто напишите мне:
- https://t.me/py_free_developer

Телеграм-канал, чтобы получать свежие новости:
- https://t.me/it_syeysk

## Links

- [Описание узлов Python](https://greentreesnakes.readthedocs.io/en/latest/nodes.html)
- [Стандарт C](http://www.open-std.org/jtc1/sc22/wg14/)
