from argparse import ArgumentParser
from pathlib import Path
from sys import stdout

from py2c.bytecode_walker import translate
from py2c.translator_cpp import TranslatorC


def trans(python_source_code, write_to):
    translator = TranslatorC(save_to=write_to)
    translate(translator, python_source_code)


def run():
    parser = ArgumentParser(
        prog='Py2C translator',
        description='The program translates python-syntax to c-syntax',
    )
    parser.add_argument(
        'input',
        nargs=1,
        type=Path,
        help='A python file to compile',
    )
    parser.add_argument(
        '-o',
        '--output',
        nargs='?',
        default=None,
        type=Path,
        help='A filename for output c-file. If absent, a name will be like <input-base-filename>.c'
    )
    parser.add_argument(
        '-p',
        '--print',
        action='store_true',
        help='If set, the program will print a output in console and output argument will be ignored',
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='v0.1.1',
        help='shows version info of Py2C',
    )

    args = parser.parse_args()
    input_filepath = args.input[0]
    with open(input_filepath) as input_file:
        python_source_code = input_file.read()

    if args.print:
        trans(python_source_code, stdout)
        return

    output_filepath = args.output
    if not output_filepath:
        output_filepath = input_filepath.parent / f'{input_filepath.stem}.c'

    with open(output_filepath, 'w') as output_file:
        trans(python_source_code, output_file)


if __name__ == '__main__':
    run()
