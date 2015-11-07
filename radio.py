#!/usr/bin/python


import time,os,sys


class display():
    def light(self,value):
        pass

    def button_pressed(self,a):
        print "pressed button %i"%a

    def button_released(self,a):
        #print "released button %i"%a
        pass
    


class console(display):
    # Regular console which works anywhere
    def __init__(self):
        import curses
        self.scr=curses.initscr()
        self.scr.keypad(1)
        print "Using console display."
        self.LEFT=260
        self.RIGHT=261
        self.SELECT=10
        
    def clear(self):
        self.scr.clear()
        self.scr.refresh()
        
    def message(self,text):
        try:
            self.scr.addstr("%s\n"%text)
        except Exception:
            print text

    def wait_for_button(self):
        return self.scr.getch()

    def teardown(self):
        import curses
        self.scr.keypad(0)
        curses.endwin()
        
class lcd(display):
    # Adafruit LCD for Raspberry Pi
    def __init__(self):
        import Adafruit_CharLCD as LCD
        self.lcd = LCD.Adafruit_CharLCDPlate()
        self.buttons = ( LCD.SELECT,
                    LCD.LEFT,
                    LCD.UP,
                    LCD.DOWN,
                    LCD.RIGHT)
        self.lcd.set_color(0, 0, 0)
        self.lcd.clear()
        self.lcd.enable_display(True)
        self.lcd.show_cursor(False)
        self.lcd.message('Ready')

        self.last_state={}
        
        self.LEFT=LCD.DOWN
        self.RIGHT=LCD.RIGHT
        self.SELECT=LCD.SELECT
        
    def light(self,value):
        self.lcd.set_color(value,value,value)

    def clear(self):
        self.lcd.clear()
        
    def message(self,text):
        self.lcd.message(text)

    def wait_for_button(self):
        print 'Waiting for button pressed'
        while True:
            # Loop through each button and check if it is pressed.
            a={}
            for button in self.buttons:
                if self.lcd.is_pressed(button):
                    a[button]=True
                else:
                    a[button]=False
            
            if self.last_state != a:
                self.last_state=a
                for i in a:
                    if a[i]==True:
                        self.button_pressed(i)
                        return i
                    else:
                        self.button_released(i)
            time.sleep(0.1)
    

    def teardown(self):
        self.light(0)
        self.clear()

try:
    disp = lcd()
except Exception:
    disp = console()

rootdir = 'music'

def walkdir():
    filelist={}

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            try:
                filelist[file]=('play',os.path.join(subdir, file))
            except Exception:
                pass

    filelist['* Up']=('menu_up')

    return filelist


stations = {#'Radio 1':'http://www.bbc.co.uk/radio/listen/live/r1_aaclca.pls',  
            'BBC Radio 1':('play','http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p'),
            'BBC Radio 2':('play','http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p'),
#            'Radio 2':'http://www.bbc.co.uk/radio/listen/live/r2_aaclca.pls',
            'BBC Radio 3':('play','http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio3_mf_p'),
            'BBC Radio 4':('play','http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4fm_mf_p'),
            'BBC Radio 5 Live':('play','http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio5live_mf_p'),
            'BBC Radio 6 Music':('play','http://bbcmedia.ic.llnwd.net/stream/bbcmedia_6music_mf_p'),
            'BBC Radio Scotland':('play','http://bbcmedia.ic.llnwd.net/stream/bbcmedia_scotlandfm_mf_p'),
            'Heart London':('play','http://media-ice.musicradio.com/HeartLondon'),
            'Jazz FM':('play','http://adsi-e-02-boh.sharp-stream.com/jazzfmmobile.mp3'),
            'NHK FM':('play','http://mfile.akamai.com/129933/live/reflector:46051.asx','-cache 250 -playlist'),
            '* MP3s':('menu',
                         walkdir()),
            '** EXIT':('EXIT'),
            '** SHUTDOWN':('SHUTDOWN')}



class playerClass():
    
    def __init__(self):
        self.state='stopped'
        self.contents=''
        
    def play(self,entry,description):
        self.stop()
        self.state='playing'
        self.contents=description

        if len(entry)==3:
            cmd,url,opts=entry
        if len(entry)==2:
            cmd,url=entry
            opts=''
        os.system("mplayer %s \"%s\" &"%(opts,url))
    def get_state(self):
        return self.state,self.contents
    def stop(self):
        if self.state=='playing': os.system("killall mplayer")
        self.state='stopped'

def radio_menu_draw_screen(entry,message="Choose station",player=None):
    if player.get_state()==('playing',entry):
        disp.light(0)
        message='Now playing'
    else:
        disp.light(1)
    disp.clear()
    disp.message("%s\n%s"%(entry,message))
    

def radio_menu(menuentries,player):
    position=0

    while True:
        menulist=menuentries.keys()
        menulist.sort()
        radio_menu_draw_screen(menulist[position],message="Choose station",player=player)
        but=disp.wait_for_button()
        if but==disp.RIGHT:
            position=position+1
            if position > len(menulist)-1: position=0
        elif but==disp.LEFT:
            position=position-1
            if position < 0: position=len(menulist)-1
        elif but==disp.SELECT:
            radio_menu_select(menuentries[menulist[position]], menulist[position], player)
            if menuentries[menulist[position]]=='menu_up': break

        else:
            print "whoops another button %s" % but
    

def radio_menu_select(entry,description,player):
    print "selected %s"%str(entry)

    if entry[0]=='play': player.play(entry,description)

    if entry[0]=='menu': radio_menu(entry[1],player)
    
    if entry=='EXIT' or entry=='SHUTDOWN':
        disp.teardown()
        player.stop()

    if entry=="SHUTDOWN":
        disp.message("Shutting down...")
        os.system("sudo /sbin/shutdown -h now")

    if entry=='EXIT' or entry=='SHUTDOWN':
        sys.exit(0)



radio_menu(stations,playerClass())
