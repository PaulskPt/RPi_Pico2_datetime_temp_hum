# File sh1107_psk_v3.py
# Script examples (see below) heavily modified by @Paulsk
# Most recent update on: 2021-12-31 16h07 PT
# 2021-12-19 The current version is for the majority a copy of: https://github.com/nemart69/sh1107-micropython/blob/main/sh1107.py
#                                  and https://github.com/raspberrypi/pico-micropython-examples/blob/master/i2c/1106oled/sh1106.py
# also: # example: waveshare_sh1107_test_v5.py
# In this version v3 modified __init__() to be able to use Writer functions (for different (e.g. bigger) fonts)
# See: https://rntlab.com/question/micropython-for-esp8266-displaying-an-image-or-other-fonts-using-on-an-ssd1306-oled-display/
#
from machine import Pin, SPI
#from framebuf  import FrameBuffer, MONO_VLSB, MONO_HMSB
import framebuf
from micropython import const
import machine, time
import struct
from common_psk import my_glbls as myglbls
mg = myglbls("dummy") # create an instance of the class object
my_debug = mg.is_bits_debug()

_dc = mg.oled_pin("DC")
_cs = mg.oled_pin("CS")
_sck = mg.oled_pin("SCK")
_mosi = mg.oled_pin("MOSI")
_rst = mg.oled_pin("RST")

_width = mg.oled_pin("WIDTH")
_height = mg.oled_pin("HEIGHT")
_rotation = mg.oled_pin("ROTATION")
_external_vcc = mg.oled_pin("EXTERNAL_VCC")

SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_DCDC_MODE = const(0xAD)
SET_MEM_MODE = const(0x20)
SET_PAGE_ADDR = const(0xB0)
SET_LOW_COLUMN_ADDRESS = const(0x00)
SET_HIGH_COLUMN_ADDRESS = const(0x10)
SET_DISP_START_LINE = const(0xDC)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_COM_PIN_CFG = const(0xDA)  # copied from peterhinch/micropython-nano-gui/blob/master/drivers/ssd1306/ssd1306.py
SET_VCOM_DESEL = const(0xDB)

TEST_CHUNK = const(8)

class SH1107(framebuf.FrameBuffer):
    #def __init__(self):
    def __init__(self, width, height, external_vcc=False, rotate=0):   
        self.width = _width
        self.height = _height
        self.rotation = _rotation
        self.external_vcc = _external_vcc
        self.dc = Pin(_dc)
        self.cs = Pin(_cs)
        self.sck = Pin(_sck)
        self.mosi = Pin(_mosi)
        self.res = Pin(_rst)
        self.disp_busy_flag = 0x80
        self.disp_on_flag = 0x40
        if my_debug:
            print("SH1107.__init__(): self.width: {}, self.height: {}, self.rotation: {}, self.external_vcc: {}".format(self.width, \
            self.height,self.rotation,self.external_vcc),end='\n')
        
        if self.width == 128 and self.height == 64:
            self.page_mode = False
        elif (self.width == 64 and self.height == 128) or (self.width == 128 and self.height == 128):
            self.page_mode = True
        else:
            raise ValueError
        self.pages = self.height // 8
        self.line_bytes = self.width // 8
        size = self.width * self.height // 8
        self.curr_buffer = bytearray(b'\x00' * size) # self.fill(0)
        self.prev_buffer = bytearray(b'\xff' * size) # force full refresh
        self.spi = SPI(0, sck=self.sck, mosi=self.mosi, baudrate=1000000)
    
        # following line partly copied from: https://github.com/micropython/micropython/blob/master/tests/extmod/framebuf1.py
        self.fbuf = framebuf.FrameBuffer(self.curr_buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.rate = 10 * 1000 * 1000
        
        self.dc.init(self.dc.OUT, value=0)
        if self.res is not None:
            self.res.init(self.res.OUT, value=0)
        if self.cs is not None:
            self.cs.init(self.cs.OUT, value=1)
        if my_debug:
            print("SH1107.__init__(): value self.spi = {}".format(self.spi),end='\n')
        #super().__init__()
        super().__init__(self.fbuf, self.width, self.height, 0)
        self.init_display()
        
    def init_display(self):
        for cmd in (
            SET_DISP |           0x00,  # off
            # address setting
            SET_MEM_MODE |       (0x00 if self.page_mode else 0x01),  # 0x00 = page, 0x01 = vertical
            # resolution and layout
            SET_DISP_START_LINE, 0x00,
            SET_SEG_REMAP |      0x00,  # 0x01 rotate 180 deg
            SET_COM_OUT_DIR |    (0x00 if self.page_mode else 0x08),  # 0x08 rotate 180 deg
            SET_MUX_RATIO,       0x7f,  # always this?
            SET_DISP_OFFSET,     0x60 if self.width != self.height else 0x00,  # offseted for 64 x 128 (Aliexpress 0.96")
            # timing and driving scheme
            SET_COM_PIN_CFG,     0x02 if self.width > 2 * self.height else 0x12,  # copied from peterhinch/micropython-nano-gui/blob/master/drivers/ssd1306/ssd1306.py
            SET_DISP_CLK_DIV,    0x50,
            SET_PRECHARGE,       0x22 if self.external_vcc else 0xf1,
            SET_VCOM_DESEL,      0x35,  # 0.77 * Vcc    # peterhinch uses value of 0x30  # 0.83 * Vcc
            SET_DCDC_MODE,       0x81,  # on, 0.6 * switch freq
            # display
            SET_CONTRAST,        0x80,  # very low to avoid uneven background  was 0x10  range: 00 - FF
            SET_ENTIRE_ON |      0x00,  # output follows RAM contents, not entire on
            SET_NORM_INV |       0x00,   # 0x00 = not inverted, 0x01 = inverted
            #SET_CHARGE_PUMP,     0x10 if self.external_vcc else 0x14,  # copied from peterhinch/micropython-nano-gui/blob/master/drivers/ssd1306/ssd1306.py
            SET_DISP | 0x01, # on -- copied from peterhinch/micropython-nano-gui/blob/master/drivers/ssd1306/ssd1306.py
        ):
            self.write_cmd(cmd)
        # buffers are initialized as if self.fill(0) was called
        self.show()
        self.poweron()
    
    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def rotate(self, flag, update=True):
        if flag:
            self.write_cmd(SET_SEG_REMAP | 0x01)  # mirror display vertically
            self.write_cmd(COM_OUT_DIR | 0x08)  # mirror display hor.
        else:
            self.write_cmd(SET_SEG_REMAP | 0x00)
            self.write_cmd(COM_OUT_DIR | 0x00)
        if update:
            self.show()

    def sleep(self, value):
        self.write_cmd(SET_DISP | (not value))
        
    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)
        
    def invert(self, invert):
        #SH1107_SPI.write_cmd(self, 0xA7)
        self.write_cmd(SET_NORM_INV | (invert & 1))  # 0x01)
        
    def fill(self, value):
        self.fbuf.fill(value)
        
    def text(self, value, h, v, clr):
        self.fbuf.text(value, h, v, clr)

    # From file nemart69_sh1107_micropython\sh1107.py
    def show(self):
        if self.page_mode:
            self.show_page_mode()
        else:
            self.show_vert_mode()
        self.prev_buffer[:] = self.curr_buffer

    # From file nemart69_sh1107_micropython\sh1107.py
    def show_page_mode(self):
        for page in range(self.pages):
            noffs = page * self.width
            for col1, col2 in self.test_modified(noffs, self.width):
                if my_debug:
                    print("show_page_mode(): col1, col2: {:" ">4d},{:" ">4d}, noffs:{:" ">4d}".format(col1,col2,noffs),end='\n')
                c = col1 - noffs
                self.write_cmd(SET_PAGE_ADDR | page)
                self.write_cmd(SET_LOW_COLUMN_ADDRESS | (c & 0x0f))
                self.write_cmd(SET_HIGH_COLUMN_ADDRESS | ((c & 0x70) >> 4))
                self.write_data(self.curr_buffer[col1 : col2])
                if my_debug:
                    print('Write offsets {:" ">4d} : {:" ">4d}, col: {:" ">4d}'.format(col1, col2, c))

    # From file nemart69_sh1107_micropython\sh1107.py  (https://github.com/nemart69/sh1107-micropython)
    def show_vert_mode(self):
        for col in range(self.height):
            noffs = col * self.line_bytes
            for page1, page2 in self.test_modified(noffs, self.line_bytes):
                self.write_cmd(SET_PAGE_ADDR | (page1 - noffs))
                self.write_cmd(SET_LOW_COLUMN_ADDRESS | (col & 0x0f))
                self.write_cmd(SET_HIGH_COLUMN_ADDRESS | ((col & 0x70) >> 4))
                self.write_data(self.buffer[page1 : page2])
                if my_debug:
                    print('Write offsets {} : {}, page: {}'.format(page1, page2, page1 - noffs))
                
    def reset(self, res):
        if res is not None:
            res(1)
            time.sleep_ms(1)
            res(0)
            time.sleep_ms(20)
            res(1)
            time.sleep_ms(20)

    def test_modified(self, offs, width):
        ptr = offs
        width += offs
        while ptr < width:
            # skip unmodified chunks
            while ptr < width and self.curr_buffer[ptr : ptr + TEST_CHUNK] == self.prev_buffer[ptr : ptr + TEST_CHUNK]:
                ptr += TEST_CHUNK

            if ptr < width:
                first = ptr
                ptr += TEST_CHUNK
                # find modified chunks
                while ptr < width and self.curr_buffer[ptr : ptr + TEST_CHUNK] != self.prev_buffer[ptr : ptr + TEST_CHUNK]:
                    ptr += TEST_CHUNK

                yield first, ptr
                ptr += TEST_CHUNK
                
    def write_cmd(self, cmd):
        #self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        if self.cs is not None:
            self.cs(1)
            self.dc(0)
            self.cs(0)
            if isinstance(cmd, (bytes, bytearray)):
                self.spi.write(cmd)
            else:
                self.spi.write(bytearray([cmd]))
            self.cs(1)
        else:
            self.dc(0)
            if isinstance(cmd, (bytes, bytearray)):
                self.spi.write(cmd)
            else:
                self.spi.write(bytearray([cmd]))
                
    def write_data(self, buf):
        #self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        if self.cs is not None:
            self.cs(1)
            self.dc(1)
            self.cs(0)
            if isinstance(buf, (bytes, bytearray)):
                self.spi.write(buf)
            else:
                self.spi.write(bytearray([buf]))
            self.cs(1)
        else:
            self.dc(1)
            if isinstance(buf, (bytes, bytearray)):
                self.spi.write(buf)
            else:
                self.spi.write(bytearray([buf]))   
