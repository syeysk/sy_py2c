from io import StringIO, TextIOWrapper


from py2c.bytecode_walker import translate
from py2c.translator_cpp import TranslatorC, TranslatorCpp


def trans(
        source_code: str | TextIOWrapper,
        translator_class,
        write_to=None,
        config: dict | None = None,
) -> str | None:
    source_code = source_code if isinstance(source_code, str) else source_code.read()
    if write_to:
        translator = translator_class(save_to=write_to, config=config)
        translate(translator, source_code)
    else:
        file_stdout = StringIO()
        translator = translator_class(save_to=file_stdout, config=config)
        translate(translator, source_code)
        return file_stdout.getvalue()


def trans_c(
        source_code: str | TextIOWrapper,
        write_to=None,
        config: dict | None = None,
) -> str | None:
    return trans(source_code, TranslatorC, write_to, config=config)


def trans_cpp(
        source_code: str | TextIOWrapper,
        write_to=None,
        config: dict | None = None,
) -> str | None:
    return trans(source_code, TranslatorCpp, write_to, config=config)


def compile_c(func):
    """Legacy decorator - translates to C but doesn't compile or swap function"""
    import inspect
    def _compile_c(*args, **kwargs):
        c_code = trans_c(inspect.getsource(func))
        c_file_path = 'temp.c'
        with open(c_file_path, 'wt', encoding='utf-8') as file_c:
            file_c.write(c_code)
            file_c.write('\n\nint main() {return 0;}\n')
        print(c_code)
        return func(*args, **kwargs)

    return _compile_c


def compileInline(func):
    """
    Decorator that compiles a Python function (and its dependencies) to C++
    using pybind11, compiles it to a binary module, and swaps the original
    function with the compiled version.

    Features:
    - Tracks and includes external function dependencies
    - Caches compiled modules based on source code hash
    - Automatically recompiles when source changes

    Example:
        @compileInline
        def myFunction(a: int, b: int) -> int:
            return a + b
    """
    import inspect
    import hashlib
    import os
    import sys
    import importlib.util
    import textwrap
    from pathlib import Path

    # Get function source and dependencies
    func_source = textwrap.dedent(inspect.getsource(func))
    func_module = inspect.getmodule(func)

    # Track dependencies (functions called from within the decorated function)
    dependencies = []
    func_globals = func.__globals__

    # Parse the function to find external calls
    import ast
    try:
        func_ast = ast.parse(func_source)
        for node in ast.walk(func_ast):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                dep_name = node.func.id
                if dep_name in func_globals and callable(func_globals[dep_name]):
                    dep_func = func_globals[dep_name]
                    # Only include Python functions, not builtins
                    if hasattr(dep_func, '__code__'):
                        try:
                            dep_source = textwrap.dedent(inspect.getsource(dep_func))
                            dependencies.append(dep_source)
                        except (OSError, TypeError):
                            pass
    except SyntaxError:
        pass

    # Combine all source code for hashing
    combined_source = '\n'.join(dependencies) + '\n' + func_source
    source_hash = hashlib.md5(combined_source.encode()).hexdigest()

    # Determine cache directory (next to the source file or in temp)
    if func_module and hasattr(func_module, '__file__') and func_module.__file__:
        module_dir = Path(func_module.__file__).parent
        cache_dir = module_dir / '__pycache__' / 'py2c_cache'
    else:
        cache_dir = Path.home() / '.cache' / 'py2c'

    cache_dir.mkdir(parents=True, exist_ok=True)

    # Module naming to avoid conflicts
    module_name = f"{func.__name__}_{source_hash[:8]}"
    module_path = cache_dir / f"{module_name}.so"
    source_cache_path = cache_dir / f"{module_name}.txt"

    # Check if cached module exists and source hasn't changed
    if module_path.exists() and source_cache_path.exists():
        with open(source_cache_path, 'r') as f:
            cached_hash = f.read().strip()

        if cached_hash == source_hash:
            # Load cached module
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec and spec.loader:
                    compiled_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(compiled_module)
                    return getattr(compiled_module, func.__name__)
            except Exception:
                pass  # If loading fails, recompile below

    # Need to compile - translate Python to C++
    try:
        cpp_code = trans_cpp(combined_source)
    except Exception as e:
        # If translation fails, fall back to original Python function
        import warnings
        warnings.warn(f"Failed to translate {func.__name__} to C++: {e}. Using Python version.")
        return func

    # Generate pybind11 wrapper code
    cpp_file = cache_dir / f"{module_name}.cpp"

    # Create pybind11 module
    pybind_code = f"""
#include <pybind11/pybind11.h>

namespace py = pybind11;

{cpp_code}

PYBIND11_MODULE({module_name}, m) {{
    m.def("{func.__name__}", &{func.__name__}, "Compiled function");
}}
"""

    with open(cpp_file, 'w') as f:
        f.write(pybind_code)

    # Compile using g++ with pybind11
    try:
        import subprocess
        import sysconfig

        python_include = sysconfig.get_path('include')
        python_lib = sysconfig.get_config_var('LIBDIR')

        # Try to find pybind11 include path
        try:
            import pybind11
            pybind11_include = pybind11.get_include()
        except (ImportError, AttributeError):
            # pybind11 not available, fall back to Python function
            import warnings
            warnings.warn(f"pybind11 not installed. Cannot compile {func.__name__}. Using Python version.")
            return func

        compile_cmd = [
            'g++',
            '-O3',
            '-Wall',
            '-shared',
            '-std=c++11',
            '-fPIC',
            f'-I{python_include}',
            f'-I{pybind11_include}',
            str(cpp_file),
            '-o', str(module_path)
        ]

        result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            import warnings
            warnings.warn(
                f"Compilation failed for {func.__name__}: {result.stderr}. Using Python version."
            )
            return func

        # Save source hash for caching
        with open(source_cache_path, 'w') as f:
            f.write(source_hash)

        # Load and return compiled function
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec and spec.loader:
            compiled_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(compiled_module)
            return getattr(compiled_module, func.__name__)
        else:
            return func

    except Exception as e:
        import warnings
        warnings.warn(f"Failed to compile {func.__name__}: {e}. Using Python version.")
        return func
