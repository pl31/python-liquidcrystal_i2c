# python-liquidcrystal_i2c

licquidcrystal_i2c is a python module for the LCD-Module *LCM1602 IIC V2*. 
More information could be found in 
[dfrobot wiki](http://www.dfrobot.com/wiki/index.php?title=I2C/TWI_LCD1602_Module_(SKU:_DFR0063)).

This module is a port of the sources found 
[here](http://www.dfrobot.com/image/data/DFR0154/LiquidCrystal_I2Cv1-1.rar).

_[Keywords: LCM1602 IIC V2, LCM IIC V2, LCD1602 I2C, V1, V2, I2C1602V2, YWROBOT, DFROBOT]_

## Install

Install directly from github (may need admin rights for `python setup.py install`):

```
git clone --depth=1 https://github.com/pl31/python-liquidcrystal_i2c.git
(cd python-liquidcrystal_i2c/ && python setup.py install)
```

## Todo

Nice to have:

- A lot of methods from the original sources are still missing, as I do not need them. 
For a complete port these should be included
- Add example code
- Add docstring
- Add automated egg creation (travis?)
