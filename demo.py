from py2c.shortcuts import trans_c, compile_c

my_python_code = '''
def hello(a: int, b: int = 5) -> string:
    return 'good' if a + b > 0 else 'not good'
'''

c_code = trans_c(my_python_code)
print(c_code)


@compile_c
def test(a: int, b: int) -> int:
    return a * b

print('result:', test(4, 6))
