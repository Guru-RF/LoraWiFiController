import time

import adafruit_displayio_sh1106
import board
import busio
import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_progressbar.verticalprogressbar import HorizontalProgressBar
from digitalio import DigitalInOut, Direction, Pull

displayio.release_displays()

# Our reset button
btn = DigitalInOut(board.GP2)
btn.direction = Direction.INPUT
btn.pull = Pull.UP

spi = busio.SPI(board.GP10, MOSI=board.GP11, MISO=board.GP12)
dc_pin = board.GP20  # any pin!
reset_pin = board.GP22  # any pin!
cs_pin = board.GP21  # any pin!


display_bus = displayio.FourWire(
    spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin, baudrate=1000000
)
display = adafruit_displayio_sh1106.SH1106(display_bus, width=127, height=64)


display.brightness = 0.01

# Fonts
small_font = "fonts/Roboto-Medium-16.bdf"
#  glyphs for fonts
glyphs = b"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: "
#  loading bitmap fonts
small_font = bitmap_font.load_font(small_font)
small_font.load_glyphs(glyphs)

# Display content
splash = displayio.Group()
display.root_group = splash

# Progress bar
prog_bar = HorizontalProgressBar((1, 1), (127, 18))
splash.append(prog_bar)

# Steps head
steps_head = Label(small_font, text="test")
steps_head.x = 28
steps_head.y = 10

# Steps taken
text_input = Label(small_font, text="Init...")
text_input.x = 1
text_input.y = 34

# Steps per hour
text_bottom = Label(small_font, text="test")
text_bottom.x = 1
text_bottom.y = 58

# Add to display
splash.append(text_bottom)
splash.append(steps_head)
splash.append(text_input)

while True:
    time.sleep(3)
