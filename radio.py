#!/usr/bin/python
# Example using a character LCD plate.
import math
import time,os

import Adafruit_CharLCD as LCD


# Initialize the LCD using the pins 
lcd = LCD.Adafruit_CharLCDPlate()
lcd.set_color(0,0,0)
lcd.clear()
lcd.enable_display(True)
lcd.show_cursor(False)
lcd.message('Ready')

stations = {#'Radio 1':'http://www.bbc.co.uk/radio/listen/live/r1_aaclca.pls',  
            'BBC Radio 1':'http://sc1.tyo.llnw.net/stream/bbcmedia_radio1_mf_p',
            'BBC Radio 2':'http://sc1.tyo.llnw.net/stream/bbcmedia_radio2_mf_p',
#            'Radio 2':'http://www.bbc.co.uk/radio/listen/live/r2_aaclca.pls',
            'BBC Radio 3':'http://www.bbc.co.uk/radio/listen/live/r3_aaclca.pls',
            'BBC Radio 4':'http://www.bbc.co.uk/radio/listen/live/r4_aaclca.pls',
            'BBC Radio 5 Live':'http://www.bbc.co.uk/radio/listen/live/r5l_aaclca.pls',
#            'Radio 6 Music':'http://www.bbc.co.uk/radio/listen/live/r6_aaclca.pls',
            'BBC Radio 6 Music':'http://sc1.tyo.llnw.net/stream/bbcmedia_6music_mf_p',
            'BBC Radio Scotland':'http://sc1.tyo.llnw.net/stream/bbcmedia_scotlandfm_mf_p',
            'Heart London':'http://media-ice.musicradio.com/HeartLondon',
            'Jazz FM':'http://adsi-e-02-boh.sharp-stream.com/jazzfmmobile.mp3',
            'NHK FM':' -cache 250  -playlist http://mfile.akamai.com/129933/live/reflector:46051.asx',
            'EXIT':'EXIT',
            'SHUTDOWN':'SHUTDOWN'}

last_state={}

def wait_for_button():
    global last_state

    buttons = ( LCD.SELECT,
                LCD.LEFT,
                LCD.UP,
                LCD.DOWN,
                LCD.RIGHT)
    print 'Waiting for button pressed'
    while True:
        # Loop through each button and check if it is pressed.
        a={}
	for button in buttons:
            if lcd.is_pressed(button):
                a[button]=True
            else:
                a[button]=False
        
        if last_state != a:
            last_state=a
            for i in a:
                if a[i]==True:
                    button_pressed(i)
                    return i
                else:
                    button_released(i)
        time.sleep(0.1)
    
def button_pressed(a):
    print "pressed button %i"%a

def button_released(a):
    #print "released button %i"%a
    pass

def radio_menu_draw_screen(pos,message="Choose station"):
    lcd.set_color(1,1,1)
    lcd.clear()
    lcd.message("%s\n%s"%(stations.keys()[pos],message))

def radio_menu():
    position=0

    radio_menu_draw_screen(position)
    while True:
        print position
        but=wait_for_button()
        if but==LCD.DOWN:
            position=position+1
            if position > len(stations)-1: position=0
            radio_menu_draw_screen(position)
        elif but==LCD.RIGHT:
            position=position-1
            if position < 0: position=len(stations)-1
            radio_menu_draw_screen(position)
#        elif but==LCD.LEFT:
#            os.system("amixer set 'Playback Digital' 5-")
#            radio_menu_draw_screen(position,"Volume down")
#        elif but==LCD.RIGHT:
#            os.system("amixer set 'Playback Digital' 5+")
#            radio_menu_draw_screen(position,"Volume up")


        elif but==LCD.SELECT:
            play_name=stations.keys()[position]
            play_url=stations[play_name]
            if (play_name=="EXIT" or play_name=="SHUTDOWN"): break
            play(play_name,play_url)
        else:
            print "whoops another button %i" % but
    
    lcd.clear()
    lcd.set_color(0,0,0)
    os.system("killall mplayer")

    if play_name=="SHUTDOWN":
        lcd.message("Shutting down...")
        os.system("sudo /sbin/shutdown -h now")


def play(name,url):
    lcd.set_color(0,0,0)
    os.system("killall mplayer")
    lcd.clear()
    lcd.message("%s\nNow playing"%name)
    if type(url)==type('str'):
        os.system("mplayer %s &"%url)
    else:
        os.system("%s &"%url[1])
    #os.system("vlc --no-interact %s &"%url)

radio_menu()
