"""
  aht_rtc_oled_test.py
  2024-10-30 11h00 PT  by @Paulskpt
  Micropython test script for a Raspberry Pi Pico 2 (RP2350)

  Hardware:
  a RPi Pico 2 stacked on a Pimoroni Pico Breakout Garden base.
  (https://shop.pimoroni.com/products/pico-breakout-garden-base?variant=32369509892179)
  The base also containing:
  - a Pimoroni BG 1.12in OLED 128x128 SPI LCD;
    (https://shop.pimoroni.com/products/1-12-oled-breakout?variant=29421050757203)
  - an Adafruit AHT20 sensor (https://www.adafruit.com/product/4566)
    via Qwiic connector and wire connected to a Pimoroni BG adapter:
    (https://shop.pimoroni.com/products/breakout-garden-to-qwiic-adaptor?variant=39308382339155)
  - a Pimoroni BG RV3028 RTC board
    (https://shop.pimoroni.com/products/rv3028-real-time-clock-rtc-breakout?variant=27926940549203)
  
  The driver for the AHT20 I encountered on Github: https://github.com/etno712/aht.

  However the creator used a strange way to update the temperature and humidity.
  He created a class "property": sensor.is_ready. This property calls the class function self._measure().
  
  For readability and intiutively understand I renamed the property to "update" instead of "is_ready".
  Secondly I changed this property into a function, as is commonly used in other libraries.
  To trigger the AHT20 sensor to calculate the sensor data, we now call: aht20.update().
  I made these changes in the file: aht.py.
  
  NOTE:
  I had the two oscilloscope probes connected to a Breakout Garden adapter with pins
  (one from the "Pimoroni Breakout Garden Extender Kit" (3 pairs):
  https://shop.pimoroni.com/en-us/products/breakout-garden-extender-kit).
  When the oscilloscope was OFF,
  and the oscilloscope probes were still connected to an I2C breakout socket (nr 2), this script crashed in file: "aht.py",
  line 67, in Status, with error: OSError: [Errno 5] EIO. When I took out the adapter with the connected probes the script
  ran without error.
  
"""
from pimoroni_i2c import PimoroniI2C # builtin in Pimoroni's micropython
from breakout_rtc import BreakoutRTC # idem
from machine import SPI, I2C, Pin
import sys
import time
from sh1107_psk_v3 import SH1107
from writer import Writer
import my_notosansregular18 # Font
from common_psk import my_glbls as myglbls
mg = myglbls("dummy") # create an instance of the class object
my_debug = mg.is_my_debug()
use_AHT20 = mg.is_use_AHT20()

print("use_AHT20 = ", end="")
print(use_AHT20)
print(f"AHT20, RV3028 and OLED: initializing...",end='\n')
if my_debug:
    print(mg.__info__(2), end='\n')
    print(mg.__info__(3), end='\n')

if use_AHT20:
    from aht import AHT2x

#PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}  # i2c pins 4, 5 for Breakout Garden
PINS_PICO_2 = {"sda": 4, "scl": 5}

#i2c = PimoroniI2C(**PINS_BREAKOUT_GARDEN)
# 0x52: rv3028-python: rv3028: rv3028 real-time-clock breakout
i2c = PimoroniI2C(**PINS_PICO_2)
rtc = BreakoutRTC(i2c)

lStart = True # startup flag (see ck_start_time(), disp_time() and main())
black = 0x0000
white = 0xFFFF
degs = chr(176)   # "°"     # extended ascii
euro = chr(8364)  #  0x20AC 

try:
    OLED = SH1107(128,128)  # 0x20AC
except Exception as e:
    print(f"Error occurred while calling SH1107() to initialize.\nError: {}".format(e),end='\n')
    raise SystemExit

wri = Writer(OLED, my_notosansregular18, verbose=False)


def disp_title():
    OLED.fill(black)
    Writer.set_textpos(OLED, 1, 10) # In case a previous test has altered this
    wri.printstring("AHT20 Temp")
    #OLED.text(b"Datetime & Temp", 5, 20, white)
    Writer.set_textpos(OLED, 1, 30) # In case a previous test has altered this
    wri.printstring("& Humidity")
    Writer.set_textpos(OLED, 1, 50) # In case a previous test has altered this
    wri.printstring("RV3028 RTC")
    Writer.set_textpos(OLED, 1, 70) # In case a previous test has altered this
    wri.printstring("Test")
    #OLED.text(b"Test",5, 40,white)
    OLED.show()

OLED.fill(white)
time.sleep(1)
disp_title()
time.sleep(2)

aht20 = None
temperature = 0.0
humidity = 0.0

disp_title()
print(f"Displaying title", end='\n')
time.sleep(3)

if use_AHT20:
    try:
        aht20 = AHT2x(i2c, crc=False)
    #except OSError as e:
    except ValueError as e:
        print("aht20 sensor seems not connected. Check please.", end='\n')
        mg.__set__(1, False)  # We will not use the aht20 sensor
        use_AHT20 = mg.is_use_AHT20()  # re-read the value
        #raise SystemExit
    print("use_AHT20 is set to: {}".format(use_AHT20), end='\n')
    # print("type(aht20) = {}".format(type(aht20)), end='\n')
        
if use_AHT20:  # NOTE This 'looks double use of use_AHT20' but it is in fact a new check after the flag will be altered at the ValueError exception
    aht20.update()
    temperature = aht20.temperature
    humidity = aht20.humidity
    print("Temperature: {:5.2f}{:s}C".format(temperature, degs), end='\n')
    print("Humidity:    {:5.2f} %rH".format(humidity), end='\n')
    
    t = "Temp: {:5.2f} {:s}C".format(temperature, degs)
    #OLED.text(t, 5, 60, white)
    h = "Hum: {:5.2f} %rH".format(humidity)
    
    Writer.set_textpos(OLED, 1, 90) # In case a previous test has altered this
    wri.printstring(t)
    Writer.set_textpos(OLED, 1, 110) # In case a previous test has altered this
    wri.printstring(h)
    OLED.show()
    time.sleep(2)

if rtc.is_12_hour():
    rtc.set_24_hour()

rtc.enable_periodic_update_interrupt(True)

def test_glyphs():
    for _ in range(8300, 8365): # (128, 1000):
        #if _ % 32 == 0:
        #    time.sleep(3)
        print("ord value: {}, chr(value): {}".format(_, chr(_)), end='\n')

def clean_2lines():
    Writer.set_textpos(OLED, 1, 90)
    txt = ' ' * 14
    wri.printstring(txt)
    Writer.set_textpos(OLED, 1, 110)
    wri.printstring(txt)
    Writer.set_textpos(OLED, 1, 90)
    
def ck_start_time():
    if rtc.update_time():
        if rtc.get_year() >= 2024:
            if lStart:
                print(f"ck_start_time(): we will use rtc datetime for start")
            return True
    return False

def disp_time():
    if rtc.update_time():
        dow_lst = mg.get_dow_lst()
        dt_old_lst = mg.get_dt_old()
        yy_o = dt_old_lst[0]
        mo_o = dt_old_lst[1]
        dd_o = dt_old_lst[2]
        
        #rtc_date = rtc.string_date()
        #rtc_time = rtc.string_time()
        yy = rtc.get_year()
        mo = rtc.get_month()
        dd = rtc.get_date()
        wd = rtc.get_weekday()
        hh = rtc.get_hours()
        mm = rtc.get_minutes()
        ss = rtc.get_seconds()
        dt_lst = [yy,mo,dd,wd,hh,mm,ss]
        # only save current datetime if lStart or (current datetime != old datetime)
        if lStart or (dt_lst != dt_old_lst):
            mg.set_dt_old(dt_lst) # save the current dt
        
        s_ymd = "{}-{:02d}-{:02d}".format(yy, mo, dd)
        s_wd = dow_lst[wd]
        s_hms = "{:02d}:{:02d}:{:02d}".format(hh, mm, ss)
        print("\n{} {}, {}".format(s_wd, s_ymd, s_hms), sep='\n')
        if lStart:
            OLED.fill(black)
            OLED.show()
        # Only update display if lStart or (year or month or date) has changed
        if lStart or ((yy != yy_o) or (mo != mo_o) or (dd != dd_o)):
            Writer.set_textpos(OLED, 1, 20) # In case a previous test has altered this
            wri.printstring(s_wd)
            Writer.set_textpos(OLED, 1, 40)
            wri.printstring(s_ymd)
        Writer.set_textpos(OLED, 1, 60) # In case a previous test has altered this
        wri.printstring(s_hms)
        OLED.show()
    else:
        print("\ncall to rtc.update_time() failed", end='\n')
        
def disp_tmp_hum():
    aht20.update()  # this calls self._measure()
    clean_2lines()
    t3 = "Temp: {:.2f} {:s}C".format(aht20.temperature, degs)
    #print()
    print(t3, end='\n')
    #OLED.text(t3, 1,60, white)
    Writer.set_textpos(OLED, 1, 90) # In case a previous test has altered this
    wri.printstring(t3)
    """ We check against a humidity value of 99.99 because the {:6.2} formatting is rounding
        the humidity to 100.00. Therefore checking against >= 100.00 fails.
        From a displayed value of 100.00 we need to make "Hum:" more short to: "H:"
        otherwise the display driver will fold the text to a new line and moves the rest of
        the text above one line upwards. This we don't want."""
    if aht20.humidity >= 99.99:  
        h3 = "H: {:6.2f} %rH".format(aht20.humidity, degs)
    else:
        h3 = "Hum: {:5.2f} %rH".format(aht20.humidity, degs)
    print(h3, end='\n')
    Writer.set_textpos(OLED, 1, 110) # In case a previous test has altered this
    wri.printstring(h3)
    OLED.show()

def main():
    global lStart
    #test_glyphs()
    delay = 1
    current_t = 0
    while True:
        try:
            if lStart:
                if not ck_start_time():
                    #                     ss,mm, hh,wD, dd, mo,   yy
                    result = rtc.set_time(0, 24, 19, 2, 30, 10, 2024)
                    print("Result of setting rtc: {}".format(result), end='\n')
            disp_time()
            lStart = False
            if use_AHT20:
                disp_tmp_hum()
        except KeyboardInterrupt:
            raise SystemExit
        except Exception as e:
            print("Error occurred: {}".format(e), end='\n')
            raise

        time.sleep(delay)
        # disp_title()

if __name__=="__main__":
    main()