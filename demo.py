from py2c.shortcuts import trans_c

my_python_code = '''
def hello(a: int, b: int = 5) -> 'const char*':
    return 'positive' if a + b > 0 else 'negative or zero'

def main() -> int:
    print(hello(-10))
    return 0
'''

c_code = trans_c(my_python_code)
print(c_code)
