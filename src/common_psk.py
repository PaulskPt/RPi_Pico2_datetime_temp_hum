# common_psk.py
# "BG" stands for Breakout Garden

class my_glbls(object):
    
    _MY_DEBUG = 0
    _USE_AHT20 = 1
    _BITS_DEBUG = 2
    _AHT20_ADS = 3
    _GLBLS_DEBUG = 4
    _USE_LED = 5

    _dc = 16
    _cs = 17  # for BG SPI socket A (front). GP22 for socket B
    _sck = 18
    _mosi = 19
    _rst = 20  # for BG SPI socket A (front). GP21 for socket B
    _width = 128
    _height = 128
    _rotation = 270
    _external_vcc = False
    
    _keys = {0:"MY_DEBUG", 1:"USE_AHT20", 2:"BITS_DEBUG", 3:"AHT20_ADS", 4:"GLBLS_DEBUG", 5:"USE_LED"}
    _okeys = {"DC": 0, "CS":1, "SCK":2, "MOSI":3, "RST":4,"WIDTH":5,"HEIGHT":6,"ROTATION":7,"EXTERNAL_VCC":8}
    _okeys2 = {0:"DC", 1:"CS", 2:"SCK", 3:"MOSI", 4:"RST",5:"WIDTH",6:"HEIGHT",7:"ROTATION",8:"EXTERNAL_VCC"}
    _dtkeys = {0:"YY", 1:"MO", 2:"DD", 3:"WD", 4:"HH", 5:"MM", 6:"SS"}
    
    def __init__(self, name):
        self.TAG = "my_glbls."
        TAG2 = '__init__() '
        self.name = name  # Just a dummy because needed at least one parameter for __init__() (besides self)
        self._glbls = {0: False, 1: True, 2: False, 3: 56, 4:False, 5:True}  # 56 dec = 0x38 hex
        self._oled =  {0:self._dc, 1:self._cs, 2:self._sck, 3:self._mosi, 4:self._rst,5:self._width,6:self._height,7:self._rotation,8:self._external_vcc}
        self._dto =   {0:2024,1:10,2:31,3:3,4:2,5:27,6:0} # dto = datetime old
        #                 0         1          2            3           4         5           6
        self._dow_lst = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        super().__init__()
        self.my_debug = self._glbls[self._GLBLS_DEBUG]  # debug flag for this file
        if self.my_debug:
            print(self.TAG+TAG2+"self._glbls: {}".format(self._glbls), end='\n')
            print(self.TAG+TAG2+"self._oled:  {}".format(self._oled),  end='\n')
            print(self.TAG+TAG2+"self._dto:   {}".format(self._dto),   end='\n')

        
    def is_my_debug(self):
         return self._glbls[self._MY_DEBUG]
        
    def is_use_AHT20(self):
        return self._glbls[self._USE_AHT20]
    
    def is_bits_debug(self):
         return self._glbls[self._BITS_DEBUG]
    
    def is_use_LED(self):
        return self._glbls[self._USE_LED]
        
    def AHT20_ads(self):
        return self._glbls[self._AHT20_ADS]
    
    def get_dt_old(self):
        return self._dto
    
    def set_dt_old(self, dt_lst):
        TAG = self.TAG + "set_dt_old(): "
        if isinstance(dt_lst, list):
            for i in range(len(dt_lst)):
                self._dto[i] = dt_lst[i]
            if self.my_debug:
                print(TAG + "param dt_lst = {}".format(dt_lst), end='\n')
                print(TAG + "saved old datetime = {}".format(list(self._dto.values())), end='\n')
        else:
            print(TAG + "datetime must be a list",end='\n')
    
    def get_dow_lst(self):
        return self._dow_lst
    
    def get_old_dt(self):
        return list(self._dto.values())
    
    def oled_pin(self, key):
        TAG = self.TAG + "oled_pin(): "
        if type(key) == str:
            if self.my_debug:
                print(TAG+"key \'key\' = {}".format(key),end='\n')
            if key in self._okeys:
                k = self._okeys[key]
                if self.my_debug:
                    print(TAG+"key \'k\' = {}".format(key),end='\n')
                if k in self._oled:
                    if self.my_debug:
                        print(TAG+"value returned for key \'{}\' is: \'{}\'".format(self._okeys2[k], self._oled[k]),end='\n')
                    return self._oled[k]
                else:
                    if self.my_debug:
                        print(TAG+"key \'{}\' not in dict '\self._oled\'".format(k),end='\n')
                    return None
            else:
                if my_debug:
                    print(TAG+"key \'{}\' not in dict '\self._okeys\'".format(key),end='\n')
                return None
        else:
            return None

    
    def __set__(self, key, value):
        TAG = self.TAG + '.__set__(): '
        if type(key) == int:
            if key in self._glbls:
                self._glbls[key] = value
            else:
                print(TAG+"key: {} not found".format(key), end='\n')
        else:
            le = len(self._glbls)
            print(TAG+"Please enter a number between 0 and {} as key to glbls dictionary".format(le), end='\n')
    
    def __info__(self, idx):
        TAG = 'my_glbls.__info__(): '
        if type(idx) == int:
            if idx == 0:
                print(TAG+"self._glbls.keys(): {}".format(self._glbls.keys()), end='\n')
            elif idx == 1:
                print(TAG+"Not yet implemented", end='\n')
            elif idx == 2:
                for _ in range(0,len(self._glbls)):
                    print(TAG+"key: {:" ">12s}, value: {}".format(self._keys[_], self._glbls[_]), end='\n')
            elif idx == 3:
                for _ in range(0,len(self._oled)):
                    print(TAG+"key: {:" ">12s}, value: {}".format(self._okeys2[_], self._oled[_]), end='\n')
            else:
                print(TAG+"Unknown choice: {}".format(idx), end='\n')
        else:
            print(TAG+"Please enter a number between 0 and 2 as key to glbls dictionary", end='\n')

                