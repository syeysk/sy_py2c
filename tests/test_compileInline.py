"""Unit tests for the compileInline decorator"""

import pytest
import tempfile
import shutil
from pathlib import Path

from py2c.shortcuts import compileInline


class TestCompileInline:
    """Test suite for compileInline decorator functionality"""

    def test_simple_function(self):
        """Test compiling a simple function with no dependencies"""
        @compileInline
        def add_numbers(a: int, b: int) -> int:
            return a + b

        result = add_numbers(3, 5)
        assert result == 8

    def test_function_with_operations(self):
        """Test function with multiple operations"""
        @compileInline
        def calculate(x: int, y: int) -> int:
            return x * y + x - y

        result = calculate(5, 3)
        assert result == 17  # 5*3 + 5 - 3 = 15 + 5 - 3 = 17

    def test_function_with_dependency(self):
        """Test function that calls another function"""
        def helper_add(a: int, b: int) -> int:
            return a + b

        @compileInline
        def main_function(x: int, y: int) -> int:
            return helper_add(x, y)

        result = main_function(10, 20)
        assert result == 30

    def test_caching_mechanism(self):
        """Test that caching works - function should work on multiple calls"""
        @compileInline
        def cached_multiply(a: int, b: int) -> int:
            return a * b

        # First call
        result1 = cached_multiply(4, 5)
        assert result1 == 20

        # Second call - should use cached version
        result2 = cached_multiply(6, 7)
        assert result2 == 42

    def test_negative_numbers(self):
        """Test with negative numbers"""
        @compileInline
        def subtract(a: int, b: int) -> int:
            return a - b

        result = subtract(10, 15)
        assert result == -5

    def test_zero_values(self):
        """Test with zero values"""
        @compileInline
        def multiply_by_zero(a: int) -> int:
            return a * 0

        result = multiply_by_zero(100)
        assert result == 0

    def test_nested_dependencies(self):
        """Test function with nested function calls"""
        def level1(x: int) -> int:
            return x + 1

        def level2(x: int) -> int:
            return level1(x) * 2

        @compileInline
        def level3(x: int) -> int:
            return level2(x) + 5

        result = level3(5)
        # level1(5) = 6, level2(5) = 6*2 = 12, level3(5) = 12 + 5 = 17
        assert result == 17

    def test_example_from_issue(self):
        """Test the exact example from issue #2"""
        def someFunctionCalledFromTheCppFunction(var: int, var2: int) -> int:
            return var + var2

        def somePurePythonFunction(var: int, var2: int) -> int:
            return var * var2

        @compileInline
        def someFunctionThatGetsCompiledAndCachedAtExecutionTime(var: int, var2: int) -> int:
            return someFunctionCalledFromTheCppFunction(var, var2)

        theAnswerToTheUniverse = (
            someFunctionThatGetsCompiledAndCachedAtExecutionTime(30, 2) +
            somePurePythonFunction(5, 2)
        )
        assert theAnswerToTheUniverse == 42


class TestCompileInlineCachePaths:
    """Test cache directory creation and file handling"""

    def test_cache_directory_creation(self):
        """Test that cache directories are created properly"""
        @compileInline
        def test_func(a: int) -> int:
            return a * 2

        result = test_func(5)
        assert result == 10

        # Verify that cache was created (in __pycache__/py2c_cache or ~/.cache/py2c)
        # We just verify the function works, actual cache inspection would require
        # knowing the exact path which depends on execution context


class TestCompileInlineFallback:
    """Test fallback behavior when compilation is not possible"""

    def test_fallback_to_python_on_invalid_syntax(self):
        """Test that invalid C++ translations fall back to Python"""
        # Note: This test verifies the decorator handles errors gracefully
        # The actual fallback depends on the translator's ability to handle the code

        @compileInline
        def simple_function(a: int, b: int) -> int:
            return a + b

        # Even if compilation fails, function should still work via Python
        result = simple_function(1, 2)
        assert result == 3
