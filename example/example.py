var1: 'unsigned int' = 10  # unsigned int var1 = 10;
var2: 'unsigned int' = None  # unsigned int var2;
var3: 'unsigned int'  # unsigned int var3;
var4: 'unsigned char' = 'a'
var5: 'unsigned char' = 20


def func1() -> 'void':  # void func1() {};
    return None


def func2(arg1: 'ann1', arg2: 'ct1' = 5, arg3: 'ct2' = 8,
          arg4: 'ann2' = 10) -> 'unsigned char':  # unsigned char func2() {};
    return 'c'


def func3() -> 'unsigned char':
    fvar: 'unsigned int2' = 78
    if fvar > 9:
        return 56
    elif fvar < 5:
        return 67

    if fvar > 9:
        fvar = 56
    elif fvar > 5:
        fvar = 67
    elif fvar > 1:
        fvar = 90
    else:
        fvar = 0

    if fvar > 9:
        fvar = 56
    else:
        fvar = 67
        fvar += 5

    return 'c', 6


var5 = func2(var5, 897) + 'test' + var4

# a = 10
# b: int = 25
# novalue: int
# yesvalue: int = a
cbf: 'unsigned int' = 10
cbf2: 'unsigned int' = cbf * (24 + var1)  # TODO: проверять все операнды на соответствие типа
cbf2 = cbf * 24 + var1
cbf2 = 24 + var1 * cbf
cbf2 = cbf - 34
cbf2 = cbf * 34
cbf2 = cbf / 34
cbf2 = cbf | 34
cbf2 = cbf or 34  # нужен ли данный код?
cd = 'g'
cd = 6
ab: 'unsigned int' = cd == 7  # бесполезный код. Если такая переменная используется в условии, то её следует заменить на смао выражение
if cd == 7:
    cbf = 15

counter: 'unsigned int' = 100
useless_action: 'unsigned int' = 0
while counter > 0:
    useless_action += 1
    if useless_action == 5:
        func2(67, 89)
        break

    if useless_action == 7:
        func1()
        continue

    counter += 1
else:
    useless_action = 0

cd += 1
cd -= 1
cd = -cd