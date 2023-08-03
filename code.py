import time
import rtc
import board
import busio
import adafruit_rfm9x
from digitalio import DigitalInOut, Direction
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import PWMOut
import adafruit_rgbled
import adafruit_requests as requests
import asyncio
import microcontroller
from adafruit_datetime import datetime
import adafruit_displayio_ssd1306
import displayio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
import rotaryio
import config

# our version
VERSION = "RF.Guru_LoraWiFiControler 0.1" 

# release displays
displayio.release_displays()

# Create the I2C interface for the oled
i2c = busio.I2C(scl=board.GP27, sda=board.GP26)

# Display bus
display_bus = displayio.I2CDisplay(i2c, device_address=60)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64, rotation=180)
display.brightness = 0.01

print(f"{VERSION}\n")

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

esp32_cs = DigitalInOut(board.GP17)
esp32_ready = DigitalInOut(board.GP14)
esp32_reset = DigitalInOut(board.GP13)

# Clock MOSI(TX) MISO(RX)
spi = busio.SPI(board.GP18, board.GP19, board.GP16)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
      print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

RED_LED = PWMOut.PWMOut(esp, 25)
GREEN_LED = PWMOut.PWMOut(esp, 26)
BLUE_LED = PWMOut.PWMOut(esp, 27)
status_light = adafruit_rgbled.RGBLED(RED_LED, GREEN_LED, BLUE_LED)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)


## Connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected!")
  
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)

# Initialize a requests object with a socket and esp32spi interface
socket.set_interface(esp)
requests.set_socket(socket, esp)

now = None
while now is None:
    try:
        now = time.localtime(esp.get_time()[0])
    except OSError:
        pass
rtc.RTC().datetime = now

wifi.pixel_status((100,100,0))
time.sleep(1)
wifi.pixel_status((0,100,0))

# Fonts
small_font = "fonts/Roboto-Medium-16.bdf"
#  glyphs for fonts
glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: '
#  loading bitmap fonts
small_font = bitmap_font.load_font(small_font)
small_font.load_glyphs(glyphs)

# Display content
splash = displayio.Group()

# Steps countdown
steps_countdown = Label(small_font, text='Left')
steps_countdown.x = 1
steps_countdown.y = 22

# Steps taken
text_steps = Label(small_font, text="0 Done    ")
text_steps.x = 1
text_steps.y = 40

# Steps per hour
text_sph = Label(small_font, text="0/H")
text_sph.x = 1
text_sph.y = 58

# Add to display
splash.append(text_sph)
splash.append(steps_countdown)
splash.append(text_steps)

display.show(splash)

knob = rotaryio.IncrementalEncoder(board.GP6, board.GP9)

while True:

    text_steps.text = '%d Done' % knob.position
    time.sleep(0.1)