# Author: Patrick Buech
# Url: https://github.com/pl31/python-liquidcrystal_i2c
# License: MIT
# Ported from: http://www.dfrobot.com/image/data/DFR0154/LiquidCrystal_I2Cv1-1.rar

import smbus
import time

class LiquidCrystal_I2C:
    # commands
    _LCD_CLEARDISPLAY = 0x01
    _LCD_RETURNHOME = 0x02
    _LCD_ENTRYMODESET = 0x04
    _LCD_DISPLAYCONTROL = 0x08
    _LCD_CURSORSHIFT = 0x10
    _LCD_FUNCTIONSET = 0x20
    _LCD_SETCGRAMADDR = 0x40
    _LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    _LCD_ENTRYRIGHT = 0x00
    _LCD_ENTRYLEFT = 0x02
    _LCD_ENTRYSHIFTINCREMENT = 0x01
    _LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    _LCD_DISPLAYON = 0x04
    _LCD_DISPLAYOFF = 0x00
    _LCD_CURSORON = 0x02
    _LCD_CURSOROFF = 0x00
    _LCD_BLINKON = 0x01
    _LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    _LCD_DISPLAYMOVE = 0x08
    _LCD_CURSORMOVE = 0x00
    _LCD_MOVERIGHT = 0x04
    _LCD_MOVELEFT = 0x00

    # flags for function set
    _LCD_8BITMODE = 0x10
    _LCD_4BITMODE = 0x00
    _LCD_2LINE = 0x08
    _LCD_1LINE = 0x00
    _LCD_5x10DOTS = 0x04
    _LCD_5x8DOTS = 0x00

    # flags for backlight control
    _LCD_BACKLIGHT = 0x08
    _LCD_NOBACKLIGHT = 0x00

    _En = 0x04  # Enable bit
    _Rw = 0x02  # Read/Write bit
    _Rs = 0x01  # Register select bit


    def __init__(self, addr, port, numlines=2, clear=True):
        self._addr = addr
        self._smbus = smbus.SMBus(port)
        self._backlightval = 0x08 # always on

        self._numlines = numlines

        # SEE PAGE 45/46 FOR INITIALIZATION SPECIFICATION!
        # according to datasheet, we need at least 40ms after power rises above 2.7V
        # before sending commands. Arduino can turn on way befer 4.5V so we'll wait 50
        time.sleep(0.050)

        # Now we pull both RS and R/W low to begin commands
        self._expanderWrite(self._backlightval); # reset expander and turn backlight off (Bit 8 =1)
        time.sleep(1)

        # put the LCD into 4 bit mode
        # this is according to the hitachi HD44780 datasheet
        # figure 24, pg 46

        # we start in 8bit mode, try to set 4 bit mode
        for _delay in [0.004500, 0.004500, 0.000150]: # wait min 4.1ms twice
            self._write4bits(0x03 << 4)
            time.sleep(_delay)

        # finally, set to 4-bit interface
        self._write4bits(0x02 << 4)

        # set # lines, font size, etc.
        _displayfunction = LiquidCrystal_I2C._LCD_4BITMODE | \
            LiquidCrystal_I2C._LCD_2LINE | LiquidCrystal_I2C._LCD_5x8DOTS
        self._command(LiquidCrystal_I2C._LCD_FUNCTIONSET | _displayfunction)

        # turn the display on with no cursor or blinking default
        self._displaycontrol = LiquidCrystal_I2C._LCD_DISPLAYON | \
            LiquidCrystal_I2C._LCD_CURSOROFF | LiquidCrystal_I2C._LCD_BLINKOFF
        self._command(LiquidCrystal_I2C._LCD_DISPLAYCONTROL | self._displaycontrol)

        # Initialize to default text direction (for roman languages)
        self._displaymode = LiquidCrystal_I2C._LCD_ENTRYLEFT | \
            LiquidCrystal_I2C._LCD_ENTRYSHIFTDECREMENT;
        # set the entry mode
        self._command(LiquidCrystal_I2C._LCD_ENTRYMODESET | self._displaymode);

        # clear it off
        if clear:
            self.clear()


    ### high level commands, for the user! ###

    def clear(self):
        self._command(LiquidCrystal_I2C._LCD_CLEARDISPLAY) # clear display, set cursor position to zero
        time.sleep(2) # this command takes a long time!

    def home(self):
        self._command(LiquidCrystal_I2C._LCD_RETURNHOME) # set cursor position to zero
        time.sleep(2) # this command takes a long time!

    def setCursor(self, col, row):
        row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]
        if row < 0 and row >= self._numlines:
            raise IndexError('Argument row out of range') # we count rows starting w/0
        self._command(LiquidCrystal_I2C._LCD_SETDDRAMADDR | \
            (col + row_offsets[row]))

    def noDisplay(self):
        self._displaycontrol &= ~LiquidCrystal_I2C._LCD_DISPLAYON
        self._command(LiquidCrystal_I2C._LCD_DISPLAYCONTROL | self._displaycontrol)

    def display(self):
        self._displaycontrol |= LiquidCrystal_I2C._LCD_DISPLAYON
        self._command(LiquidCrystal_I2C._LCD_DISPLAYCONTROL | self._displaycontrol)

    def noBacklight(self):
        self._backlightval = LiquidCrystal_I2C._LCD_NOBACKLIGHT
        self._expanderWrite(0);

    def backlight(self):
        self._backlightval = LiquidCrystal_I2C._LCD_BACKLIGHT
        self._expanderWrite(0);

    # print string at cursor
    def printstr(self, value):
        for c in value:
            self._send(ord(c), 0x01)

    # print line starting at linenr #0
    def printline(self, linenr, value):
        self.setCursor(0, linenr)
        self.printstr(value)

    ### mid level commands, for sending data/cmds ###

    def _command(self, value):
        self._send(value, 0);


    ### low level data pushing commands ###

    # write either command or data
    def _send(self, value, mode):
        highnib = value & 0xf0
        lownib=(value << 4) & 0xf0
        self._write4bits(highnib | mode)
        self._write4bits(lownib | mode)

    def _write4bits(self, value):
        self._expanderWrite(value)
        self._pulseEnable(value)

    def _expanderWrite(self, data):
        self._smbus.write_byte(self._addr, data | self._backlightval)

    def _pulseEnable(self, data):
        self._expanderWrite(data | LiquidCrystal_I2C._En) # En high
        time.sleep(0.000001) # enable pulse must be >450ns

        self._expanderWrite(data | ~LiquidCrystal_I2C._En) # En low
        time.sleep(0.000050) # commands need > 37us to settle
