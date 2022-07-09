"""Testing examples from the book Белов А. В. "Разработка устройств на микроконтроллерах" """

import unittest

from tests.py2c_test_case import Py2CTestCase


SOURCE_MAIN = """
from avr.io import *
#from avr.io23113 import *
from util.delay import *
from avr.interrupt import *

\"\"\"
#define SET_BIT(byte, bit) ((byte) |= (1UL << (bit)))
#define CLEAR_BIT(byte,bit) ((byte) &= ~(1UL << (bit)))
#define IS_SET(byte,bit) (((byte) & (1UL << (bit))) >> (bit))
//#define IS_SET(byte,bit) (((byte) >> (bit)) & 1)
\"\"\"

from .indic import *
from .DHT import *

I: preproc = 7

dht_data: uint8_t__4

mode: int = 1
indic: int = 2

t_min: int = 1659
t_max: int = 1947
t_fact: int = 1756

DHT_PORT: preproc = PORTB
DHT_DDR: preproc = DDRB
DHT_PIN: preproc = PINB
DHT_BIT: preproc = PB5


datadht: uint8_t__5  # массив для значений датчика
byte: 'typedef__unsigned int'  # TODO: использовать питоновский стиль для задания нового типа

def dhtread() -> int:
    j: byte = 0  # локальные переменные
    i: byte = 0  # локальные переменные
    datadht[0] = datadht[1] = datadht[2] = datadht[3] = datadht[4] = 0

    # Шаг №1

    SET_BIT(DHT_DDR, DHT_BIT)  # выход
    CLEAR_BIT(DHT_PORT, DHT_BIT)  # низкий уровень — подтягиваем линию - разбудим датчик
    _delay_ms(18)  # 18 мс по условиям документации. В принципе в ходе экспериментов я ставил задержку 30 мс, то существенной разницы не почувствовал.
    _delay_us(40)  # задержка по условию

    SET_BIT(DHT_PORT, DHT_BIT)  # отпускаем линию

    # Шаг №2

    SET_BIT(DHT_DDR, DHT_BIT)  # вход
    #while(IS_SET(DHT_PIN, DHT_BIT)) {}
    if IS_SET(DHT_PIN, DHT_BIT):
        return 12  # датчик должен ответить 0

    return 2

    _delay_us(80)  # задержка
    if not IS_SET(DHT_PIN, DHT_BIT):
        return 0  # по истечению 80 мкс, датчик должен отпустить шину
    
    return 3

    # Высокий сигнал на линии продлится также приблизительно 80 мкс

    # Шаг №3

    while IS_SET(DHT_PIN, DHT_BIT):  # ждем пока контроллер датчика начнет передавать данные
        pass

    # передача начинается с нуля
    for j in range(0, 5):
        datadht[j] = 0
        for i in range(0, 8):
            cli ()  # запрещаем прерывания
            while not SET(DHT_PIN, DHT_BIT):  # ждем когда датчик отпустит шину
                pass
 
            _delay_us (30)  # задержка высокого уровня при 0 30 мкс
            if IS_SET(DHT_PIN, DHT_BIT):  # если по истечению времени сигнал на линии высокий, значит передается 1
                datadht[j] |= 1<<(7-i)  # тогда i-й бит устанавливаем 1
                
            while IS_SET(DHT_PIN, DHT_BIT):  # ждем окончание 1
                pass
                
            sei ()  # разрешаем общее прерывание

    return 1


def manage(t_min: int, t_max: int, t_fact: int):
    pass

def get_t_fact() -> int:
    # return dht_fetchData(dht_data)
    return dhtread()
	# return dht_data[0] + dht_data[1] + dht_data[2] + dht_data[3] + dht_data[4]

\"\"\"
ISR(PCINT_vect){
	_delay_ms(1);
	if (IS_SET(PINB, 4)) {
	    indic += 1;
	    if (indic > 2) indic = 0;
	}
}
\"\"\"
def main() -> int:
    PORTA=0xFF
    DDRA=0xFF
    PORTB=0x00
    DDRB=0b11101111
    PORTD=0xFF
    DDRD=0xFF

    SET_BIT(SREG, I)

    SET_BIT(GIMSK, PCIE)
    SET_BIT(PCMSK, PCINT4)
 
    #initDHT()
    _delay_ms(500)

    while True:
        CLEAR_BIT(SREG, I)
        t_fact = get_t_fact()
        SET_BIT(SREG, I)
        if indic == 0:  # min
            display_change(t_min)
        elif indic == 1:  # max
            display_change(t_max)
        elif indic == 2:  # fact
            display_change(t_fact)

        display_show()
    	# guess, to turn off or to turn on heater
        manage(t_min, t_max, t_fact)
        _delay_us(900)

    return 0
"""
RESULT_MAIN = """#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>

#define SET_BIT(byte, bit) ((byte) |= (1UL << (bit)))
#define CLEAR_BIT(byte,bit) ((byte) &= ~(1UL << (bit)))
#define IS_SET(byte,bit) (((byte) & (1UL << (bit))) >> (bit))
//#define IS_SET(byte,bit) (((byte) >> (bit)) & 1)

#include "./indic.h"
//s#include "./DHT.h"

#define I 7

uint8_t dht_data[4];

int mode = 1;
int indic = 2;

int t_min = 1659;
int t_max = 1947;
int t_fact = 1756;

#define DHT_PORT PORTB
#define DHT_DDR DDRB
#define DHT_PIN PINB
#define DHT_BIT PB5

uint8_t datadht[5]; /* массив для значений датчика*/
typedef unsigned int byte;

int dhtread ()
{
        byte j = 0, i = 0; /*локальные переменные*/
        datadht[0] = datadht[1] = datadht[2] = datadht[3] = datadht[4] = 0 ;

        /*Шаг №1*/

        SET_BIT(DHT_DDR, DHT_BIT); // выход
        CLEAR_BIT(DHT_PORT, DHT_BIT); /*низкий уровень — подтягиваем линию-       разбудим датчик*/
        _delay_ms (18); /*18 мс по условиям документации. В принципе в ходе экспериментов я ставил задержку 30 мс, то существенной разницы не почувствовал. */
        _delay_us (40); /*задержка по условию*/
        SET_BIT(DHT_PORT, DHT_BIT); /*отпускаем линию*/

        /*Шаг №2*/

        SET_BIT(DHT_DDR, DHT_BIT); // вход
        //while(IS_SET(DHT_PIN, DHT_BIT)) {}
        if (IS_SET(DHT_PIN, DHT_BIT)) { return 12; } //датчик должен ответить 0
        return 2;

        _delay_us (80); // задержка
        if (!IS_SET(DHT_PIN, DHT_BIT)) { return 0; } /*по истечению 80 мкс, датчик должен отпустить шину*/
        return 3;

        /*Высокий сигнал на линии продлится также приблизительно 80 мкс*/

        /*Шаг№3*/

         while (IS_SET(DHT_PIN, DHT_BIT)); /* ждем пока контроллер датчика начнет передавать данные*/

         //передача начинается с нуля
         for (j=0; j<5; j++)
          {
                 datadht[j]=0;
                 for (i=0; i<8; i++)
                 {
                          cli (); // запрещаем прерывания
                          while (!IS_SET(DHT_PIN, DHT_BIT));   /* ждем когда датчик отпустит шину */
                          _delay_us (30); /*задержка высокого уровня при 0 30 мкс*/
                          if (IS_SET(DHT_PIN, DHT_BIT)) /*если по истечению времени сигнал на линии высокий, значит передается 1*/
                                       datadht[j]|=1<<(7-i); /*тогда i-й бит устанавливаем 1*/
                          while (IS_SET(DHT_PIN, DHT_BIT));  // ждем окончание 1
                          sei ();// разрешаем общее прерывание
                  }
          }
          return 1;
}

void manage(int t_min, int t_max, int t_fact) {

}

int get_t_fact() {
    //return dht_fetchData(dht_data);
    return dhtread();
	//return dht_data[0] + dht_data[1] + dht_data[2] + dht_data[3] + dht_data[4];

}

ISR(PCINT_vect){
	_delay_ms(1);
	if (IS_SET(PINB, 4)) {
	    indic += 1;
	    if (indic > 2) indic = 0;
	}
}

int main(void) {
    PORTA=0xFF;
    DDRA=0xFF;
    PORTB=0x00;
    DDRB=0b11101111;
    PORTD=0xFF;
    DDRD=0xFF;

    SET_BIT(SREG, I);

    SET_BIT(GIMSK, PCIE);
    SET_BIT(PCMSK, PCINT4);

    //initDHT();
    _delay_ms(500);

    while (1)
    {

        CLEAR_BIT(SREG, I);
    	t_fact = get_t_fact();
        SET_BIT(SREG, I);

    	if (indic == 0) { // min
    		display_change(t_min);
    	} else if (indic == 1) { // max
    		display_change(t_max);
    	} else if (indic == 2) { // fact
    		display_change(t_fact);
    	}
    	display_show();

    	// guess, to turn off or to turn on heater
    	manage(t_min, t_max, t_fact);

    	_delay_us(900);
    }

    return 0;
}
"""

SOURCE_INDIC = """
from avr.io import *
from util.delay import *

#def SET_BIT(byte: 'int', bit: 'int') -> None: byte |= (t1UL << (bit))
SET_BIT: preproc = lambda byte, bit: '((byte) |= (1UL << (bit)))'
CLEAR_BIT: preproc = lambda byte, bit: '((byte) &= ~(t1UL << (bit)))'
IS_SET: preproc = lambda byte, bit: '(((byte) & (t1UL << (bit))) >> (bit))'

display_number: 'unsigned char__auto' = [
  0x3f, #  0
  0x06, #  1
  0x5b, #  2
  0x4f, #  3
  0x66, #  4
  0x6d, #  5
  0x7d, #  6
  0x07, #  7
  0x7f, #  8
  0x6f,  #  9
]

display_digit: 'unsigned int' = 0
display_digits: 'unsigned int__link__4';

def display_change(display_value: 'unsigned int'):
    if display_digit == 0:
        display_digits[0] = ~(display_number[display_value / 1000])
    elif display_digit == 1:
        display_digits[1] = ~(display_number[(display_value / 100) % 10])
    elif display_digit == 2:
        display_digits[2] = ~(display_number[(display_value / 10) % 10])
    elif display_digit == 3:
        display_digits[3] = ~(display_number[display_value % 10])


def display_show():
    PORTD = display_digits[display_digit]

    #//PINB.1 = (digit >> 3) && 1;
    #//PORTB2 = (digit >> 2) && 1;
    #//PORTB3 = (digit >> 1) && 1;
    #//PORTB4 = (digit >> 0) && 1;
    PORTB &= 0b11110000
    SET_BIT(PORTB, display_digit)

    display_digit += 1
    if display_digit > 3:
        display_digit = 0
"""

RESULT_INDIC = """#include <avr/io.h>
#include <util/delay.h>

#define SET_BIT(byte, bit) ((byte) |= (1UL << (bit)))
#define CLEAR_BIT(byte,bit) ((byte) &= ~(1UL << (bit)))
#define IS_SET(byte,bit) (((byte) & (1UL << (bit))) >> (bit))
//#define IS_SET(byte,bit) (((byte) >> (bit)) & 1)


unsigned char display_number[] =
{
  0x3f, //0
  0x06, //1
  0x5b, //2
  0x4f, //3
  0x66, //4
  0x6d, //5
  0x7d, //6
  0x07, //7
  0x7f, //8
  0x6f  //9
};

unsigned int display_digit = 0;
unsigned int* display_digits[4];

void display_change(unsigned int display_value) {
    if (display_digit == 0) display_digits[0] = ~(display_number[display_value / 1000]);
    else if (display_digit == 1) display_digits[1] = ~(display_number[(display_value / 100) % 10]);
    else if (display_digit == 2) display_digits[2] = ~(display_number[(display_value / 10) % 10]);
    else if (display_digit == 3) display_digits[3] = ~(display_number[display_value % 10]);
}

void display_show() {
	PORTD = display_digits[display_digit];

    //PINB.1 = (digit >> 3) && 1;
    //PORTB2 = (digit >> 2) && 1;
    //PORTB3 = (digit >> 1) && 1;
    //PORTB4 = (digit >> 0) && 1;
    PORTB &= 0b11110000;
    SET_BIT(PORTB, display_digit);

    display_digit += 1;
    if (display_digit > 3) display_digit = 0;
}
"""


class AuthorsProjectTestCase(Py2CTestCase):
    @unittest.skip('The source code is not ready for transformin into the original result')
    def test_main(self):
        self.assertSuccess(SOURCE_MAIN, RESULT_MAIN)

    @unittest.skip('The source code is not ready for transformin into the original result')
    def test_indic(self):
        self.assertSuccess(SOURCE_INDIC, RESULT_INDIC)


if __name__ == '__main__':
    unittest.main()
