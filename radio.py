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

    root_paths=os.listdir(rootdir)
    root_paths.sort()
    for p in root_paths:
        dirpath=os.path.join(rootdir, p)
        if os.path.isdir(dirpath):
            subdir=os.listdir(dirpath)
            subdir.sort()
            subdir=[os.path.join(dirpath,i) for i in subdir]
            subdfilelist="'"+"' '".join(subdir)+"'" 
            filelist[p]=('play',subdfilelist)

    filelist['* Up']=('menu_up')

    return filelist

stations = {  
            'BBC Radio 1':('play','http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_radio_one.m3u8'),
            'BBC Radio 1 Relax':('play','http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_radio_one_relax.m3u8'),
            'BBC Radio 2':('play','http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_radio_two.m3u8'),
            'BBC Radio 3':('play','http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_radio_three.m3u8'),
            'BBC Radio 4':('play','http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_radio_fourfm.m3u8'),
            'BBC Radio 5 Live':('play','http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_radio_five_live.m3u8'),
            'BBC Radio 6 Music':('play','http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_6music.m3u8'),
            'BBC Radio Scotland':('play','http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/uk/sbr_high/ak/bbc_radio_scotland_fm.m3u8'),
            'Jazz FM':('play','http://edge-bauerall-01-gos2.sharp-stream.com/jazzhigh.aac'),
            'WFMU New Jersey':('play','http://stream0.wfmu.org/freeform-high.aac'),
            'FluxFM Berlin':('play','http://streams.fluxfm.de/live/mp3-320/audio/play.m3u'),
            'Flux Lounge':('play','http://streams.fluxfm.de/lounge/mp3-320/audio/play.m3u'),
            'Flux Chillhop':('play','http://streams.fluxfm.de/Chillhop/mp3-320/streams.fluxfm.de/play.m3u'),
            'Flux Euro Jazz':('play','http://streams.fluxfm.de/Euro/mp3-320/streams.fluxfm.de/play.m3u'),
            'SomaFM GS Classic':('play','http://somafm.com/nossl/gsclassic130.pls'),
            'SomaFM Drone Zone':('play','http://somafm.com/nossl/dronezone130.pls'),
            'SomaFM Groove Salad':('play','http://somafm.com/nossl/groovesalad130.pls'),
            'SomaFM Space Station':('play','http://somafm.com/nossl/spacestation130.pls'),
            '* MP3s':('menu',
                         walkdir()),
            '** EXIT':('EXIT'),
            '** SHUTDOWN':('SHUTDOWN')}



# The above streams are restricted to the UK. For the international stream when available,
# replace /uk/ with /nonuk/ and /sbr_med/ with /sbr_low/ or /sbr_vlow/.
# Different bitrates are available by replacing /sbr_med/ :
# /sbr_vlow/ = 48k /sbr_low/ = 96k
# UK only: /sbr_med/ = 128k /sbr_high/ = 320k

# e.g.  http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_6music.m3u8


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
        # later versions need mplayer -allow-dangerous-playlist-parsing 
        os.system("cvlc %s %s &"%(opts,url))
    def get_state(self):
        return self.state,self.contents
    def stop(self):
        if self.state=='playing': os.system("killall mplayer vlc")
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
