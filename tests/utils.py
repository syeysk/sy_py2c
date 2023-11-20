from io import StringIO

from py2c.bytecode_walker import translate
from py2c.translator_cpp import TranslatorC, TranslatorCpp


def trans_c(source_code):
    file_stdout = StringIO()
    translator = TranslatorC(save_to=file_stdout)
    translate(translator, source_code)
    return file_stdout.getvalue()


def trans_cpp(source_code):
    file_stdout = StringIO()
    translator = TranslatorCpp(save_to=file_stdout)
    translate(translator, source_code)
    return file_stdout.getvalue()