Example of using class:

```python
from microcontrollers import MC

mc = MC('stm8s')
mc.cpu.freq = 45000000
mc.i2c.on = True
mc.i2c.speed = 125000
mc.porta_6.io = MC.AIN  # AIN - analog input, DOUT - digital output
mc.porta_7.write(128)
mc.porta_6.io = MC.DOUT
value = mc.porta_6.read()
```