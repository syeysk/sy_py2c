from tiny2313 import CLKPR, CLKPR, PIND_0, PINB_0, PORTB_0
from delay import delay_us


def main() -> 'void':
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
