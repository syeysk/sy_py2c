"""Testing examples from the book Белов А. В. "Разработка устройств на микроконтроллерах" """
from py2c.shortcuts import trans_c as trans

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
RESULT_LISTING_4_4 = """#include "tiny2313.h"

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

RESULT_LISTING_4_6 = """#include "delay.h"
#include "tiny2313.h"

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

RESULT_LISTING_4_8 = """#include "delay.h"
#include "tiny2313.h"

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


class TestExamples:
    def test_example4_4(self):
        assert trans(SOURCE_LISTING_4_4) == RESULT_LISTING_4_4

    def test_example4_6(self):
        assert trans(SOURCE_LISTING_4_6) == RESULT_LISTING_4_6

    def test_example4_8(self):
        assert trans(SOURCE_LISTING_4_8) == RESULT_LISTING_4_8
