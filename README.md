# Translator from Python into C ([русская версия](README.ru.md))

Use Python-syntax to write a clear C-code for your microcontrollers

![](doc/this-py2c-translator.png)

[About another variants of Python to C translating](docs/another_translaters.md)

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

## Install/Uninstall

Use this command to install Py2C:
```bash
pip install git+https://github.com/syeysk/tool_py2c_translator.git
```

Use this command to uninstall Py2C:
```bash
pip uninstall py2c
```

## Function's and class' description

`py2c.shortcuts.trans_c(source_code, write_to=None)` - translate a python-code into c-code. Arguments:
- `source_code` - a source python-code like unicode string (type of `str`) or text file object (returning `open` function)
- `write_to` - a file object to write a result c-code. If `write_to` is `None` (as default), the function will return the c-code as string (type of `str`)

`py2c.TranslatorC(save_to)` - class of python-to-c translator. Contains some methods to translate constructions. Arguments:
- `save_to` - a file object to write the result c-code

`py2c.translate(translator, source_code: str)` - convert `source_code` into AST, walk it and build c-code. Arguments:
- `translator` - a instance of translator. For example, `py2c.TranslatorC` or `py2c.TranslatorCpp`
- `source_code` - a source python-code (type of `str`)

## Command line interface examples

You can use `py2c` or `python -m py2c` equivalently.

Create *your_source_code.c* with c-code:
```bash
py2c your_source_code.py
```

Create *your_output_code.c* with c-code:
```bash
py2c your_source_code.py -o your_output_code.c
```

Print c-code into console:
```bash
py2c your_source_code.py -p
```

# ROADMAP

[Roadmap](ROADMAP.md)

## Contacts

If you need help, ask me:
- https://t.me/py_free_developer

Telegram to get fresh news:
- https://t.me/syeysk_it

## Links

- [Description of Python nodes](https://greentreesnakes.readthedocs.io/en/latest/nodes.html)
- [Standard of C](http://www.open-std.org/jtc1/sc22/wg14/)
