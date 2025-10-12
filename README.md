# Translator from Python into C ([русская версия](README.ru.md))

Use Python-syntax to write a clear C-code for your microcontrollers:

![](docs/this-py2c-translator.png)

[About another variants of Python to C translating](docs/another_translaters.md)

## Examples

Translate Python into C:

```python
from py2c.shortcuts import trans_c

print(trans_c('''
def hello(a: int, b: int = 5) -> 'const char*':
    return 'positive' if a + b > 0 else 'negative or zero'

def main() -> int:
    print(hello(-10))
    return 0
'''))
```

This will be printed:
```c
#include "stdio.h"

const char* hello(int a, int b) {
    return (a + b > 0) ? "positive" : "negative or zero";
}
const char* hello(int a) {
    return hello(a, 5);
}
int main(void) {
    printf(hello(-10));
    return 0;
}
```

Without shortcuts if you want more control:

```python
from py2c.bytecode_walker import translate
from py2c.translator_cpp import TranslatorC

my_python_code = '''
def hello(a: int, b: int = 5) -> 'const char*':
    return 'positive' if a + b > 0 else 'negative or zero'

def main() -> int:
    print(hello(-10))
    return 0
'''

with open('c_code.c') as c_file:
    translator = TranslatorC(save_to=c_file)
    translate(translator, my_python_code)
```


Translate Python into C and run this C-code from Python:

```python
from py2c.shortcuts import inline_c


def someFunctionCalledFromTheCppFunction(var: int, var2: int) -> int:
    return var + var2


def somePurePythonFunction(var: int, var2: int) -> int:
    return var * var2


@inline_c
def someFunctionThatGetsCompiledAndCachedAtExecutionTime(var: int, var2: int) -> int:
    return someFunctionCalledFromTheCppFunction(var, var2)


theAnswerToTheUniverse: int = someFunctionThatGetsCompiledAndCachedAtExecutionTime(30, 2) + somePurePythonFunction(5, 2)
print(f"theAnswerToTheUniverse: {theAnswerToTheUniverse}")
```

Output: `theAnswerToTheUniverse: 42`

## Demo

Translate, compile and run per one time:
```bash
python3 demo.py 1> demo.c && g++ demo.c && g++ demo.c && ./a.out
```

Run Python-code and C-code together:
```bash
python3 demo_inline_c.py
```

## Install/Uninstall

Use this command to install Py2C:
```bash
pip install git+https://github.com/syeysk/sy_py2c.git
apt install python3.11-dev
```

Write your python version instead of `python3.11`.

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

## Roadmap

[Roadmap](ROADMAP.md)

## Support

Get help, make issue or discuss Py2C:
- https://t.me/sy_py2c

Get fresh news about another my projects:
- https://t.me/syeysk_it

## Links

- [Description of Python nodes](https://greentreesnakes.readthedocs.io/en/latest/nodes.html)
- [Standard of C](http://www.open-std.org/jtc1/sc22/wg14/)
