"""Testing examples from the book Белов А. В. "Разработка устройств на микроконтроллерах" """

import unittest

from tests.py2c_test_case import Py2CTestCase


SOURCE_LISTING_4_4 = """
from tiny2313 import *


def main():
    CLKPR = 0x80
    CLKPR = 0x00

    while True:
        while PIND_0 == 1:
            pass

        # if PINB_0 == 1:
        #     PORTB_0 = 0
        # else:
        #     PORTB_0 = 1

        PORTB_0 = 0 if PINB_0 == 1 else 1

        while PIND_0 == 1:
            pass
"""
RESULT_LISTING_4_4 = """#include <tiny2313.h>

void main(void) {
    CLKPR = 128;
    CLKPR = 0;
    while (1) {
        while (PIND_0 == 1) {
        }

        PORTB_0 = (PINB_0 == 1) ? 0 : 1;
        while (PIND_0 == 1) {
        }

    }

}
"""

SOURCE_LISTING_4_6 = """
from tiny2313 import *
from delay import *


def main():
    CLKPR = 0x80
    CLKPR = 0x00

    while True:
        while PIND_0 == 1:
            pass

        delay_us(200)
        PORTB_0 = 0 if PINB_0 == 1 else 1
        while PIND_0 == 1:
            pass

        delay_us(200)
"""

RESULT_LISTING_4_6 = """#include <tiny2313.h>

#include <delay.h>

void main(void) {
    CLKPR = 128;
    CLKPR = 0;
    while (1) {
        while (PIND_0 == 1) {
        }

        delay_us(200);
        PORTB_0 = (PINB_0 == 1) ? 0 : 1;
        while (PIND_0 == 1) {
        }

        delay_us(200);
    }

}
"""

SOURCE_LISTING_4_8 = """
from tiny2313 import *
from delay import *


def main():
    PORTB = 0xFF
    DDRB = 0xFF
    PORTD = 0x7F
    DDRD = 0x00
    ACSR = 0x80
    while True:
        if PIND_0 == 1:
            PORTB_0 = 1
        else:
            PORTB_0 = 1
            delay_ms(200)
            PORTB_0 = 0
            delay_ms(200)
"""

RESULT_LISTING_4_8 = """#include <tiny2313.h>

#include <delay.h>

void main(void) {
    PORTB = 255;
    DDRB = 255;
    PORTD = 127;
    DDRD = 0;
    ACSR = 128;
    while (1) {
        if (PIND_0 == 1) {
            PORTB_0 = 1;
        } else {
            PORTB_0 = 1;
            delay_ms(200);
            PORTB_0 = 0;
            delay_ms(200);
        }

    }

}
"""


class ExamplesTestCase(Py2CTestCase):
    def test_example4_4(self):
        self.assertSuccess(SOURCE_LISTING_4_4, RESULT_LISTING_4_4)

    def test_example4_6(self):
        self.assertSuccess(SOURCE_LISTING_4_6, RESULT_LISTING_4_6)

    def test_example4_8(self):
        self.assertSuccess(SOURCE_LISTING_4_8, RESULT_LISTING_4_8)


if __name__ == '__main__':
    unittest.main()
