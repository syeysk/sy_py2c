ac: int = 6
ab: float = 9
def hello(a: int, b: int = 5) -> string:
    return 'good' if a + b > 0 else 'not good'