"""
Example demonstrating the compileInline decorator usage.

This example is based on the feature request in issue #2.
"""

from py2c.shortcuts import compileInline


def someFunctionCalledFromTheCppFunction(var: int, var2: int) -> int:
    return var + var2


def somePurePythonFunction(var: int, var2: int) -> int:
    return var * var2


@compileInline
def someFunctionThatGetsCompiledAndCachedAtExecutionTime(var: int, var2: int) -> int:
    return someFunctionCalledFromTheCppFunction(var, var2)


# Test the compiled function
theAnswerToTheUniverse: int = someFunctionThatGetsCompiledAndCachedAtExecutionTime(30, 2) + somePurePythonFunction(5, 2)
print(f"theAnswerToTheUniverse: {theAnswerToTheUniverse}")

# Expected output: 42 (30+2 + 5*2 = 32 + 10 = 42)
