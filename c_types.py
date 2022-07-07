"""
list of c-types:
- "int" is build-in int ((int),)
- "float" is build-in float ((float),)

"""

from typing import NewType, Union

char = Union[str, int]  # ((str, 1), (int, 0, 255))
short = NewType('short', int)
long = NewType('long', int)
double = NewType('double', float)
