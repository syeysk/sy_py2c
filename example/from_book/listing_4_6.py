from tiny2313 import CLKPR, CLKPR, PIND_0, PINB_0, PORTB_0
from delay import delay_us


def main() -> 'void':
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
