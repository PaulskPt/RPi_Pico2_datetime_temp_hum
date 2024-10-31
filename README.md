
REPO: RPi_Pico2_datetime_temp_hum

by @PaulskPt (Github) 2024

License: MIT

This is a project to show datetime, temperature and humidity values on an OLED display.

The Micropython script runs on a Raspberry Pi Pico 2.

Firmware:
Pimoroni-pico-rp2350 [repo](https://github.com/pimoroni/pimoroni-pico-rp2350)
  
Script by @PaulskPt
- main.py by @PaulskPt
- common_psk.py by @PaulskPt
- my_notosansregular18.py by @PaulskPt, generated by font_to_py.py
  
Parts by others:

- writer.py (c) 2019-2021 Peter Hinch (version 0.5.0)
  [repo](https://github.com/peterhinch/micropython-font-to-py/blob/master/writer/writer.py).
- aht.py by Jonathan Fromentin (Github etno712) [repo](https://github.com/etno712/aht/blob/main/aht.py), changes by @PaulskPt
- sh1107_psk_v3.py original by Nemart69 [repo](https://github.com/nemart69/sh1107-micropython), 
  changes by @PaulskPt

The used font ```my_notosansregular18.py``` was created using Peter Hinch's 
"font_to_py" [repo](https://github.com/peterhinch/micropython-font-to-py/tree/master).
The font is a global font collection downloaded from ```Google Fonts```: 
[font](https://fonts.google.com/noto/specimen/Noto+Sans).

Hardware:
  a Raspberry Pi Pico 2 stacked onto a Pimoroni Pico Breakout Garden base.
  [info](https://shop.pimoroni.com/products/pico-breakout-garden-base?variant=32369509892179)
  
  The base also containing:
  - a Pimoroni BG 1.12in OLED 128x128 SPI LCD;
    [info](https://shop.pimoroni.com/products/1-12-oled-breakout?variant=29421050757203)
  - an Adafruit AHT20 sensor [info](https://www.adafruit.com/product/4566),
    via a Qwiic connector and wire connected to a Pimoroni BG adapter:
    [info](https://shop.pimoroni.com/products/breakout-garden-to-qwiic-adaptor?variant=39308382339155)
  - a Pimoroni BG RV3028 RTC board
    [info](https://shop.pimoroni.com/products/rv3028-real-time-clock-rtc-breakout?variant=27926940549203)
	
	
This micropython script is a port from another script I created in 2021.
The script is now running on a Raspberry Pi Pico 2 (RP2035)

What the script does:

After applying power the script create an instance of the class my_glbls (in common_psk.py).
This class is used to store and retrieve variables and values.
It is my way to try to minimize the use of global variables.
From this my_glbls class varios variables are set.
The script creates instances of:

```
Instance name:  Class:         File:
mg              myglbls        common_psk.py
i2c             PimoroniI2C    firmware Pimoroni-pico-rp2350
rtc             BreakoutRTC    same
OLED            SH1107         sh1107_psk_v3.py
wri             Writer         writer.py
aht20           AHT2x          aht.py
```

Next the scipt calls disp_title() to put an intro text onto the display.
The script then gets values from the AHT20 sensor by calling aht20.update()
and setting variables: temperature and humidity, then print the values to the
Shell (or Serial Monitor) and shows them on the display.
Next the rtc is set for a 24hour clock and set "rtc.enable_periodic_update_interrupt".
Next the function main() takes control. With an interval of 1 second 
the values of datetime, temperature and humidity are printed to the Shell and are 
shown on the display.
Loop() calls the function disp_time().
This function first reads the datetime from the realtime clock. It compares the datetime
values with those saved before in the my_glbls class (file: common_psk.py).
If the values for date differ, the date will be shown on the display.
The values of hours, minutes and seconds will be shown every time.
If the current datetime differs from the datetime saved before,
the current datetime will be saved in the my_glbls class.
If the RV3028 realtime clock does not have a datetime with year of 2024 or higher,
this is an indication that the datetime in rtc memory is incorrect.
In that case the rtc will be set from a hardcoded datetime in loop(),
a datetime the user has to set once, for example as shown in:

```
#                               ss,mm, hh,wD, dd, mo,   yy
line 244: result = rtc.set_time(0, 24, 19, 2, 30, 10, 2024)
```

Note that in function ```disp_time()```, a day-of-the-week list is
read from the myglbls class by:

```
dow_lst = mg.get_dow_lst()
```

In file ```common_psk.py``` the list is defined as follows:
```
        #                 0         1          2            3           4         5           6
        self._dow_lst = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
```

and the function to retrieve this list:
```
    def get_dow_lst(self):
        return self._dow_lst
```

Because the realtime clock board has a backup battery, 
the datetime set will not be lost. The rtc will continue to update the 
datetime when the Raspberry Pi Pico 2 is not powered.
During the loop the date values are only displayed/refreshed at startup
and when the date has changed. This makes the appearance of the display
less nervous.

The script has also a function "test_glyphs()" which can be called from main().
Default the call to text_glyphs() is commented out. 
The script sets a degrees character, variable name "degs", defined as: chr(176) (= extended ascii).
The script also sets an Euro character, variable name "euro", defined as: chr(8364) (0x20AC).
However the euro character is not used in this script.


Note about script crash:

During the creation of the script and measurement of the I2C communication, I had two oscilloscope probes connected to a Breakout Garden adapter with five pins
(one from the "Pimoroni Breakout Garden Extender Kit":
[BG extender kit](https://shop.pimoroni.com/en-us/products/breakout-garden-extender-kit).
When the oscilloscope was switched off, and the oscilloscope probes were still connected to one of the four I2C breakout sockets of the Pimoroni Breakout Garden base, the script crashed in file: "aht.py",
line 67, in Status, with error: OSError: [Errno 5] EIO. 
When I removed the BG extender board with the connected probes the script executed without error.

IDE:

To create, test and upload the script and the other python files to the Pico2, I made use of the IDE: Thonny, version 174:29.

Docs: 

Serial Monitor (Shell in Thonny) output files are in the folder "docs".

Images:

Images of the hardware setup and of I2C signals are in the folder "images".
