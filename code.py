import time
import rtc
import board
import busio
import adafruit_rfm9x
from digitalio import DigitalInOut, Direction, Pull
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
from adafruit_datetime import datetime
import supervisor
import binascii
import config

# button
button = DigitalInOut(board.GP2)
button.direction = Direction.INPUT
button.pull = Pull.UP

# release displays
displayio.release_displays()

# Create the I2C interface for the oled
i2c = busio.I2C(scl=board.GP27, sda=board.GP26)

# Display bus
display_bus = displayio.I2CDisplay(i2c, device_address=60)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64, rotation=180)
display.brightness = 0.01
display.root_group[0].hidden = False
display.root_group[1].hidden = True # logo
display.root_group[2].hidden = True # status bar
supervisor.reset_terminal(display.width, 90)
display.root_group[0].y = 0

# our version
print("RF.Guru\nLoraWiFiControler 0.1") 

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
esp.set_hostname(config.hostname)

#if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
#      print("ESP32 found and in idle mode")
#print("Firmware vers.", esp.firmware_version)
#print("MAC addr:", [hex(i) for i in esp.MAC_address])

RED_LED = PWMOut.PWMOut(esp, 25)
GREEN_LED = PWMOut.PWMOut(esp, 26)
BLUE_LED = PWMOut.PWMOut(esp, 27)
status_light = adafruit_rgbled.RGBLED(RED_LED, GREEN_LED, BLUE_LED)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

## Connect to WiFi
print("Connecting to WiFi..")
wifi.connect()
  
print("Connected to:\n", str(esp.ssid, "utf-8"), "\nRSSI:", esp.rssi)

# Initialize a requests object with a socket and esp32spi interface
socket.set_interface(esp)
requests.set_socket(socket, esp)

print("Sync time with NTP!")
now = None
while now is None:
    try:
        now = time.localtime(esp.get_time()[0])
    except OSError:
        pass
rtc.RTC().datetime = now
print("Time is in sync!")

# Lora Stuff
RADIO_FREQ_MHZ = 868.775
CS = DigitalInOut(board.GP21)
RESET = DigitalInOut(board.GP20)
spi = busio.SPI(board.GP10, MOSI=board.GP11, MISO=board.GP8)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ, baudrate=1000000, agc=False,crc=True)
rfm9x.tx_power = 5

# Fonts
small_font = "fonts/spleen-16x32.bdf"
#  glyphs for fonts
glyphs = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.: '
#  loading bitmap fonts
small_font = bitmap_font.load_font(small_font)
small_font.load_glyphs(glyphs)

# Display content
splash = displayio.Group()

# Antenna
sel_antenna = Label(small_font, text="SelAnt")
sel_antenna.x = 1
sel_antenna.y = 45

# Antenna
clock = Label(small_font, text="HH:MM:SS")
clock.x = 1
clock.y = 10

# Add to display
splash.append(sel_antenna)
splash.append(clock)

display.show(splash)

knob = rotaryio.IncrementalEncoder(board.GP6, board.GP7)

nrTCPPorts = len(config.TCPports)
nrLORAPorts = len(config.LORAports)

oldTCPpos = -1
oldLORApos = -1
lora = False
while True:
    current = time.localtime()
    time_display = "{:02d}:{:02d}".format(current.tm_hour, current.tm_min)

    if button.value is False:
        if lora is False:
            lora = True
        else:
            lora = False
        print('test')
        time.sleep(1)

    if lora is True:
        clock.text = '%s W' % time_display
        TCPposition = knob.position % nrTCPPorts
        if TCPposition is not oldTCPpos:
            wifi.pixel_status((0,100,100))
            oldTCPpos = TCPposition
            sel_antenna.text = '%s' % config.TCPports[TCPposition]['name']
            try:
                requests.get(config.TCPports[TCPposition]['httpReq'], timeout=5)
            except RuntimeError:
                sel_antenna.text = 'TCPerr!'
                time.sleep(0.5)
                sel_antenna.text = 'Reboot..'
                time.sleep(0.5)
                microcontroller.reset()
            except:
                sel_antenna.text = 'Timeout'
        else:
            try:
                wifi.pixel_status((0,100,0))
            except BrokenPipeError:
                sel_antenna.text = 'NINAerr!'
                time.sleep(0.5)
                sel_antenna.text = 'Reboot..'
                time.sleep(0.5)
                microcontroller.reset()
    else:
        clock.text = '%s L' % time_display
        LORAposition = knob.position % nrLORAPorts
        if LORAposition is not oldLORApos:
            wifi.pixel_status((0,100,100))
            oldLORApos = LORAposition
            sel_antenna.text = '%s' % config.LORAports[LORAposition]['name']
            rfm9x.send(
                bytes("{}".format("<"), "UTF-8") + binascii.unhexlify("AA") + binascii.unhexlify("01") +
                bytes("{}".format(config.LORAports[LORAposition]['LoRaReq']), "UTF-8")
            )
        else:
            try:
                wifi.pixel_status((0,100,0))
            except BrokenPipeError:
                sel_antenna.text = 'NINAerr!'
                time.sleep(0.5)
                sel_antenna.text = 'Reboot..'
                time.sleep(0.5)
                microcontroller.reset()

    time.sleep(0.01)