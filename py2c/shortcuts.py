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
