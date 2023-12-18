#!/usr/bin/python3


import time,os,sys


class display():
    def light(self,value):
        pass

    def button_pressed(self,a):
        print ("pressed button %s"%a)

    def button_released(self,a):
        #print "released button %s"%a
        pass
    


class console(display):
    # Regular console which works anywhere
    def __init__(self):
        import curses
        self.scr=curses.initscr()
        self.scr.keypad(1)
        print ("Using console display.")
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
            print (text)

    def wait_for_button(self):
        return self.scr.getch()

    def teardown(self):
        import curses
        self.scr.keypad(0)
        curses.endwin()
        
class lcd(display):
    # Adafruit LCD for Raspberry Pi
    def __init__(self):
        import board
        import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

        lcd_columns = 16
        lcd_rows = 2

        i2c = board.I2C()  # uses board.SCL and board.SDA
        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

        self.lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)

        self.lcd.clear()
        self.lcd.cursor=False

        self.last_state={}
        
        self.button_label = ( 'left','right','select' )
        self.LEFT,self.RIGHT, self.SELECT=self.button_label

        self.button_state = (lambda x: self.lcd.down_button,lambda x: self.lcd.right_button,lambda x: self.lcd.select_button)
        self.buttons=dict(zip(self.button_label,self.button_state))
        
    def light(self,value):
        if value != 0: value=100
        self.lcd.color= [value,value,value]

    def clear(self):
        self.lcd.clear()
        
    def message(self,text):
        self.lcd.message = text

    def wait_for_button(self):
        print ('Waiting for button pressed')
        while True:
            # Loop through each button and check if it is pressed.
            a={}
            for button in self.buttons:
                if self.buttons[button](0):
                    a[button]=True
                else:
                    a[button]=False
            #print(a)
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
    # MPEG-DASH streams, needs VLC v3
    'BBC Radio 1':('play','https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/uk/pc_hd_abr_v2/cfs/bbc_radio_one.mpd'),
    'BBC Radio 1 Relax':('play','https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/uk/pc_hd_abr_v2/cfs/bbc_radio_one_relax.mpd'),
    'BBC Radio 2':('play','https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/uk/pc_hd_abr_v2/cfs/bbc_radio_two.mpd'),
    'BBC Radio 3':('play','https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/uk/pc_hd_abr_v2/cfs/bbc_radio_three.mpd'),
    'BBC Radio 4':('play','https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/uk/pc_hd_abr_v2/cfs/bbc_radio_fourfm.mpd'),
    'BBC Radio 5 Live':('play','https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/uk/pc_hd_abr_v2/cfs/bbc_radio_five_live.mpd'),
    'BBC Radio 6 Music':('play','https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/uk/pc_hd_abr_v2/cfs/bbc_6music.mpd'),
    'BBC Radio Scotland':('play','https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/audio/simulcast/dash/uk/pc_hd_abr_v2/cfs/bbc_radio_scotland_fm.mpd'),
    # HLS streams
    # 'BBC Radio 1':('play','http://as-hls-uk-live.akamaized.net/pool_904/live/uk/bbc_radio_one/bbc_radio_one.isml/bbc_radio_one-audio%3d128000.norewind.m3u8'),
    # 'BBC Radio 1 Relax':('play','http://as-hls-uk-live.akamaized.net/pool_904/live/uk/bbc_radio_one_relax/bbc_radio_one_relax.isml/bbc_radio_one_relax-audio%3d128000.norewind.m3u8'),
    # 'BBC Radio 2':('play','http://as-hls-uk-live.akamaized.net/pool_904/live/uk/bbc_radio_two/bbc_radio_two.isml/bbc_radio_two-audio%3d128000.norewind.m3u8'),
    # 'BBC Radio 3':('play','http://as-hls-uk-live.akamaized.net/pool_904/live/uk/bbc_radio_three/bbc_radio_three.isml/bbc_radio_three-audio%3d320000.norewind.m3u8'),
    # 'BBC Radio 4':('play','http://as-hls-uk-live.akamaized.net/pool_904/live/uk/bbc_radio_fourfm/bbc_radio_fourfm.isml/bbc_radio_fourfm-audio%3d128000.norewind.m3u8'),
    # 'BBC Radio 5 Live':('play','http://as-hls-uk-live.akamaized.net/pool_904/live/uk/bbc_radio_five_live/bbc_radio_five_live.isml/bbc_radio_five_live-audio%3d128000.norewind.m3u8'),
    # 'BBC Radio 6 Music':('play','http://as-hls-uk-live.akamaized.net/pool_904/live/uk/bbc_6music/bbc_6music.isml/bbc_6music-audio%3d128000.norewind.m3u8'),
    # 'BBC Radio Scotland':('play','http://as-hls-uk-live.akamaized.net/pool_904/live/uk/bbc_radio_scotland_fm/bbc_radio_scotland_fm.isml/bbc_radio_scotland_fm-audio%3d128000.norewind.m3u8'),
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
    'Venice Classic':('play','http://116.202.241.212:8010/stream'),
    'Swiss Classic DE':('play','http://stream.srg-ssr.ch/m/rsc_de/aacp_96'),
    'Swiss Classic FR':('play','http://stream.srg-ssr.ch/m/rsc_fr/aacp_96'),
    'Swiss Jazz':('play','http://stream.srg-ssr.ch/m/rsj/aacp_96'),    
    'TW Classical FM':('play','https://onair.family977.com.tw:8977/live.mp3'),
    'RTHK Radio 4':('play','http://stm.rthk.hk/radio4'),
    #12345678901234567890
    'Klassik Nature':('play','http://stream.klassikradio.de/nature/mp3-128'),
    'Klassik Piano':('play','http://stream.klassikradio.de/piano/mp3-128'),
    'Klassik Lounge':('play','http://stream.klassikradio.de/lounge/mp3-128'),
    'Klassik Lounge Beat':('play','http://stream.klassikradio.de/lounge-beat/mp3-128'),
    'Klassik Healing':('play','http://stream.klassikradio.de/healing/mp3-128'),
    'Klassik Smooth':('play','http://stream.klassikradio.de/smooth/mp3-128'),
    'NPO Radio 4':('play','http://icecast.omroep.nl/radio4-sb-mp3'),
    'RFr Musique':('play','https://stream.radiofrance.fr/francemusique/francemusique_hifi.m3u8?id=radiofrance'),
    'RFr Easy Class':('play','https://stream.radiofrance.fr/francemusiqueeasyclassique/francemusiqueeasyclassique_hifi.m3u8?id=radiofrance'),
    'RFr Baroque':('play','https://stream.radiofrance.fr/francemusiquebaroque/francemusiquebaroque_hifi.m3u8?id=radiofrance'),
    'RFr Labo':('play','https://stream.radiofrance.fr/francemusiquelabo/francemusiquelabo_hifi.m3u8?id=radiofrance'),
    'RFr Classic Pl':('play','https://stream.radiofrance.fr/francemusiqueclassiqueplus/francemusiqueclassiqueplus_hifi.m3u8?id=radiofrance'),
    'RFr Opera':('play','https://stream.radiofrance.fr/francemusiqueopera/francemusiqueopera_hifi.m3u8?id=radiofrance'),
    'RFr Concerts':('play','https://stream.radiofrance.fr/francemusiqueconcertsradiofrance/francemusiqueconcertsradiofrance_hifi.m3u8?id=radiofrance'),
    'RFr Jazz':('play','https://stream.radiofrance.fr/francemusiquelajazz/francemusiquelajazz_hifi.m3u8?id=radiofrance'),
    'RFr Contempo.':('play','https://stream.radiofrance.fr/francemusiquelacontemporaine/francemusiquelacontemporaine_hifi.m3u8?id=radiofrance'),
    'RFr Ocora Monde':('play','https://stream.radiofrance.fr/francemusiqueocoramonde/francemusiqueocoramonde_hifi.m3u8?id=radiofrance'),
    'RAI Radio 5':('play','http://icestreaming.rai.it/5.mp3'),
    'Sverige R P2 Musik ':('play','http://http-live.sr.se/p2musik-mp3-192'),
#    '':('play',''),
    
    
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
        os.system("cvlc -q %s %s 2> /dev/null&"%(opts,url))
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
    last_button=None
    while True:
        menulist=list(menuentries.keys())
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
            if but==last_button and player.state=='playing' and not 'menu' in menuentries[menulist[position]]:
                player.stop() # select twice, so stop
            else:
                radio_menu_select(menuentries[menulist[position]], menulist[position], player)
            if menuentries[menulist[position]]=='menu_up': break

        else:
            print ("whoops another button %s" % but)
        last_button=but
    

def radio_menu_select(entry,description,player):
    print ("selected %s"%str(entry))

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
