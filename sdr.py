#!/usr/bin/python2.7
#
# Raspberry Pi Full HD HDMI Photo Frame Carousel with SDR Radio and Internet Radio
# Copyright (C) 2018  OTTStreamingVideo.net, Toqana Consulting, LLC (A Nevada Limited Liability Company)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import sys
import os
import sdl2.ext
from flask import Flask, render_template, request, jsonify, Response
import time
import datetime
from flask_socketio import SocketIO, send, emit
from subprocess import check_output, CalledProcessError
import eventlet
eventlet.monkey_patch()
import json
import datetime
import subprocess
import imagesize
import math
from PIL import Image
from resizeimage import resizeimage
import shutil

#
# parameters
#

freqNumber                  = '104500000'   # startup FM station
freqText                    = 'FM 104.5'

sub_radio                   = 0
sub_cvlc                    = 0

ip_html                     = ''

thread_carouselFindFiles    = 0
thread_carouselDisplay      = 0

oldArray                    = []

inFolder                    = 'inFolder'
inArray                     = []
inRefreshSeconds            = 15

displayFolder               = 'displayFolder'
displayArray                = []
displayDelaySeconds         = 10

x_max                       = 1920
y_max                       = 1080

txtLine1                    = 'OTTStreamingVideo.net'
txtLine2                    = datetime.datetime.now().strftime("%A %B %d, %Y    %I:%M %p") # will be updated for every image
txtLine3                    = 'Photo by Your Name Here'
#txtLine4                    = '' # see below findIP()

#
# initialization
#

os.popen("sudo pkill -9 rtl_fm")

#
# set volume to 90%
#

command  = 'amixer sset Master playback 59000'

print command

FNULL       = open(os.devnull, 'w')
sub_amixer  = subprocess.Popen(command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)


#
# play FM station upon startup, SDR does not require Internet bandwidth
#

command  = 'rtl_fm -M wbfm -f ' + freqNumber +  ' -s 768000 -r 96000 -E deemp | '
command += "aplay -c 2 -r 48000 -f S16_LE "   # for RPi play only, do not use for browser with m3u8
command += '&> /dev/null &'

print command

FNULL       = open(os.devnull, 'w')
sub_radio  = subprocess.Popen(command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

#
# functions
#

def findIP():
    
    def get_ifconfig(iface):

        try:
            return check_output(["/sbin/ifconfig", iface], shell=True)

        except CalledProcessError as e:
            print('get_ifconfig ERROR = ' + e.message)
            return 'IP not available'

    ifconfigText = get_ifconfig("")

    if ifconfigText == 'IP not available':
        return 'IP not available'
        
    lines = ifconfigText.split('\n')
    
    html = ''

    for line in lines :
        
        line = line.strip()
        
        if line.find('inet ') == 0 :
            
            lineArr = line.split(' ')
            
            ipArr = lineArr[1].split('.')
            
            if ipArr[0] != '127':

                html += lineArr[1]
        
    return html

ip_html     = findIP()

txtLine4    = freqText + '    http://' + ip_html + '/'


#
# initialize flask with websockets
#

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')


#
# display images in displayFolder
#

def carouselDisplay():
    
    global displayFolder, displayArray, displayDelaySeconds, freqText, x_max, y_max, txtLine1, txtLine2, txtLine3, txtLine4
    
    sdl2.ext.init()

    RESOURCES            = sdl2.ext.Resources(__file__, "displayFolder")

    print sdl2.ext.get_image_formats()

    fontPathBold        = '/usr/lib/jvm/jdk-8-oracle-arm32-vfp-hflt/jre/lib/oblique-fonts/LucidaTypewriterBoldOblique.ttf'
    ManagerFontBold     = sdl2.ext.FontManager(font_path = fontPathBold, size = 20, color = (0, 0, 0))          # black

    fontPathRegular     = '/usr/lib/jvm/jdk-8-oracle-arm32-vfp-hflt/jre/lib/fonts/LucidaSansRegular.ttf'
    ManagerFontRegular  = sdl2.ext.FontManager(font_path = fontPathRegular, size = 16, color = (0, 0, 0))          # black

    #~ window              = sdl2.ext.Window("Carousel", size=(1720, 880), flags=sdl2.SDL_WINDOW_BORDERLESS)       # for debug
    window              = sdl2.ext.Window("Carousel", size=(1920, 1080), flags=sdl2.SDL_WINDOW_BORDERLESS)
    window.DEFAULTPOS   = (0, 0)
    
    window.show()

    factory             = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    spriterenderer      = factory.create_sprite_render_system(window)
    
    #
    # use first image in displayFolder
    #
    
    displayArray    = os.listdir(displayFolder)
    displayArray.sort()

    sprite              = factory.from_image(RESOURCES.get_path(displayArray[0]))

    while True:
        
        i = 1
        
        for f in displayArray:
            
            print
            print 'display number: ' + str(i) + ' of ' + str(len(displayArray)) + ', file: ' + f
            print
        
            sprite          = factory.from_color(sdl2.ext.Color(0, 0, 0), size=(1920,1080))
            sprite.position = 0, 0
            spriterenderer.render(sprite)    

            #
            # center image
            #
            
            width, height = imagesize.get('./' + displayFolder + '/' + f)
            print 'width: ' + str(width) + ', height: ' + str(height)
            
            x = math.trunc((1920 - width) / 2)
            y = math.trunc((1080 - height) / 2)
                            
            sprite          = factory.from_image(RESOURCES.get_path(f))
            sprite.position = x, y
            spriterenderer.render(sprite)
            
            sprite          = factory.from_text(txtLine1,fontmanager=ManagerFontBold)
            sprite.position = x + 40, y + 60
            spriterenderer.render(sprite)
                    
            txtLine2        = datetime.datetime.now().strftime("%A %B %d, %Y    %I:%M %p") # update for every image
            sprite          = factory.from_text(txtLine2,fontmanager=ManagerFontRegular)
            sprite.position = x + 40, y + 85
            spriterenderer.render(sprite)

            sprite          = factory.from_text(txtLine3,fontmanager=ManagerFontRegular)
            sprite.position = x + 40, y + 110
            spriterenderer.render(sprite)

            sprite          = factory.from_text(txtLine4,fontmanager=ManagerFontRegular)
            sprite.position = x + 40, y + 135
            spriterenderer.render(sprite)
                  
            time.sleep(displayDelaySeconds)
            
            i += 1
            
    processor = sdl2.ext.TestEventProcessor()
    processor.run(window)

    sdl2.ext.quit()


#
# look for new images in inFolder, resize if necessary, and copy to displayFolder
#

def carouselFindFiles():
    
    global inFolder, inArray, displayFolder, displayArray, inRefreshSeconds, x_max, y_max, oldArray, thread_carouselDisplay
    
    while True:
        
        inArray     = os.listdir(inFolder)
        print 'inArray before sort: ' + str(inArray)
        print 'len(inArray) before sort: ' + str(len(inArray))
                
        inArray.sort()
        print 'inArray after sort: ' + str(inArray)
        print 'len(inArray) after sort: ' + str(len(inArray))

        oldArray     = os.listdir(displayFolder)
        print 'oldArray before sort: ' + str(oldArray)
        print 'len(oldArray) before sort: ' + str(len(oldArray))
                
        oldArray.sort()
        print 'oldArray after sort: ' + str(oldArray)
        print 'len(oldArray) after sort: ' + str(len(oldArray))
                
        #
        # if filenames in inFolder are not equal to filenames in displayFolder
        #
        #   delete all files in displayFolder
        #
        #   copy resized (if necessary) files to displayFolder
        #
        
        if cmp(inArray, oldArray) != 0:
            
            command = 'rm -f ./' + displayFolder + '/*'
            os.popen(command)
            
            i = 1
                
            for f in inArray:
                
                #
                # resize image if necessary
                #
            
                print
                print 'resize number: ' + str(i) + ' of ' + str(len(inArray)) + ', file: ' + f
                print
                
                i += 1
            
                inFile          = './' + inFolder + '/' + f
                print 'inFile: ' + inFile
                
                displayFile     = './' + displayFolder + '/' + f
                print 'displayFile: ' + displayFile 
                
                width, height = imagesize.get(inFile)
                print 'inFolder: ' + f + ', width: ' + str(width) + ', height: ' + str(height)
                print 'inFolder: ' + f + ', x_max: ' + str(x_max) + ', y_max: ' + str(y_max)
                
                
                if width <= x_max and height <= y_max: # no resize require, just copy file
                        
                    shutil.copyfile( inFile, displayFile )
                    print 'width <= x_max and height <= y_max: no resize require, just copy file'
                
                elif width > x_max and height <= y_max:
                    
                    new_x   = x_max
                    new_y   = math.trunc((float(x_max) / width) * height)
                    
                    print 'resize width > x_max && height <= y_max: ' + f + ', new_x: ' + str(new_x) + ', new_y: ' + str(new_y)
                    
                    with open(inFile, 'r+b') as inFile:
                        
                        with Image.open(inFile) as image:
                            
                            cover = resizeimage.resize_cover(image, [new_x, new_y])
                            cover.save(displayFile, image.format)
                    
                elif width <= x_max and height > y_max:

                    new_x   = math.trunc((float(y_max) / height) * height)
                    new_y   = y_max
                    
                    print 'resize width <= x_max && height > y_max: ' + f + ', new_x: ' + str(new_x) + ', new_y: ' + str(new_y)
                    
                    with open(inFile, 'r+b') as inFile:
                        
                        with Image.open(inFile) as image:
                            
                            cover = resizeimage.resize_cover(image, [new_x, new_y])
                            cover.save(displayFile, image.format)

                elif width > x_max and height > y_max:
                    
                    if (width / x_max ) > (height / y_max):
                        
                        new_x   = x_max
                        new_y   = math.trunc((float(x_max) / width) * height)
                        
                        print 'resize (width / x_max ) > (height / y_max): ' + f + ', new_x: ' + str(new_x) + ', new_y: ' + str(new_y)
                        
                        with open(inFile, 'r+b') as inFile:
                            
                            with Image.open(inFile) as image:
                                
                                cover = resizeimage.resize_cover(image, [new_x, new_y])
                                cover.save(displayFile, image.format)                    
                
                    elif (width / x_max ) <= (height / y_max):
                        
                        new_x   = math.trunc((float(y_max) / height) * width)
                        new_y   = y_max
                        
                        print '(width / x_max ) <= (height / y_max): ' + f + ', new_x: ' + str(new_x) + ', new_y: ' + str(new_y)
                        
                        with open(inFile, 'r+b') as inFile:
                            
                            with Image.open(inFile) as image:
                                
                                cover = resizeimage.resize_cover(image, [new_x, new_y])
                                cover.save(displayFile, image.format)
                                
                    else: # no resize require, just copy file
                        
                        shutil.copyfile( inFile, displayFile )
                        print 'else: no resize require, just copy file'
                
                width, height = imagesize.get('./' + displayFolder + '/' + f)
                print 'displayFolder: ' + f + ', width: ' + str(width) + ', height: ' + str(height)                
                
            displayArray    = os.listdir(displayFolder)
            displayArray.sort()
            
            print 'displayArray: ' + str(displayArray)
            print 'len(displayArray): ' + str(len(displayArray))
            
            time.sleep(1) # reduce RPi heat and make print output more human readable for debug
            
            #
            # start carousel when resizing is completed
            #
            
            thread_carouselDisplay = socketio.start_background_task(carouselDisplay)
            print 'after resizing: thread_carouselDisplay:' + str(thread_carouselDisplay)

        #
        # start carousel if it has not already been started
        #
        
        if thread_carouselDisplay == 0:

            thread_carouselDisplay = socketio.start_background_task(carouselDisplay)
            print 'no resizing: thread_carouselDisplay:' + str(thread_carouselDisplay)            
        
        time.sleep(inRefreshSeconds)
        

thread_carouselFindFiles = socketio.start_background_task(carouselFindFiles)
print 'thread_carouselFindFiles:' + str(thread_carouselFindFiles)



#~ thread_carouselDisplay = socketio.start_background_task(carouselDisplay)
#~ print 'thread_carouselDisplay:' + str(thread_carouselDisplay)


def freqUpdate():
    
    global freqText, freqNumber
    
    while True:
        
        ts = datetime.datetime.now().strftime("%A %B %d, %Y %I:%M:%S %p")
        
        jsonStr  = '{ "freqNumber" : "' + str(freqNumber)  + '", "freqText" : "' + str(freqText)  + '", "timestamp" : "' +  str(ts) + '" }'
              
        #~ print 'freqUpdate() jsonStr = ' + jsonStr
        
        socketio.emit('freqUpdate', data=jsonStr, broadcast=True)
        
        eventlet.sleep(1)

thread_freqUpdate = socketio.start_background_task(freqUpdate)

print 'thread_freqUpdate: ' + str(thread_freqUpdate)


@app.route('/')
def index():
    
    global freqText, freqNumber, ip_html
    
    ip_html     = findIP()
    
    url         = "http://" + ip_html + "/"
    
    return render_template('index.html', url=url)


@app.route('/ajaxChannel', methods=['GET', 'POST'])
def newChannel():

    newFreq = None
    if request.method == "POST":
        newChannel  = request.json['newChannel']
        newFreq     = request.json['newFreq'] 

    global freqText, freqNumber, sub_radio, sub_cvlc
    
    freqNumber  = newFreq
    freqText    = newChannel

    if hasattr(sub_radio, 'pid'):
        sub_radio.kill()

    if hasattr(sub_cvlc, 'pid'):
        sub_cvlc.kill()
                    
    print 'newChannel() newChannel = ' + newChannel
    
    os.popen("pkill -9 rtl_fm")
    os.popen("pkill -9 vlc")

    #
    # cvlc command
    #
    
    if newChannel == 'KCRW':
        
        stream   = 'http://media.kcrw.com/pls/kcrwsimulcast.pls'
        command  = '/usr/bin/cvlc --no-video --stereo-mode=1 --gain=0.1 -I dummy ' + stream + ' &'
        
    elif newChannel == 'Classic Rock':
    
        stream   = 'https://control.internet-radio.com:2199/tunein/majesticjukebox.pls'
        command  = '/usr/bin/cvlc --no-video --stereo-mode=1 --gain=0.1 -I dummy ' + stream + ' &'    
    
    else:   #default is KUSC
        
        stream   = 'http://96.mp3.pls.kusc.live'
        command  = '/usr/bin/cvlc --no-video --stereo-mode=1 --gain=0.1 -I dummy ' + stream + ' &'

    print command

    FNULL       = open(os.devnull, 'w')
    sub_cvlc    = subprocess.Popen(command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

    resp = jsonify({"freqNumber"    : freqNumber ,
                    "freqText"      : freqText 
    })
    
    return resp


@app.route('/ajaxFM', methods=['GET', 'POST'])
def tuneFM():

    newFreq = None
    if request.method == "POST":
        newFreq = request.json['newFreq']    

    global freqText, freqNumber, sub_radio, sub_cvlc
    
    freqNumber  = newFreq

    freqText    = "FM " + freqNumber

    if hasattr(sub_radio, 'pid'):
        sub_radio.kill()

    if hasattr(sub_cvlc, 'pid'):
        sub_cvlc.kill()
    
    print 'tuneFM() newFreq = ' + newFreq
    
    os.popen("pkill -9 rtl_fm")
    os.popen("pkill -9 vlc")

    #
    # SDR rtl_fm command
    #
    
    command  = 'rtl_fm -M wbfm -f ' + freqNumber +  ' -s 768000 -r 96000 -E deemp | '
    command += "aplay -c 2 -r 48000 -f S16_LE "
    command += '&> /dev/null &'
    
    print command
    
    FNULL       = open(os.devnull, 'w')
    sub_radio   = subprocess.Popen(command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

    resp = jsonify({"freqNumber"    : freqNumber ,
                    "freqText"      : freqText 
    })

    return resp


@app.route('/ajaxFire', methods=['GET', 'POST'])
def tuneFire():
    
    global freqText, freqNumber, sub_radio, sub_cvlc
    
    freqNumber  = "Scan Fire Band"
    
    freqText    = "Scan Fire Band"
    
    if hasattr(sub_radio, 'pid'):
        sub_radio.kill()

    if hasattr(sub_cvlc, 'pid'):
        sub_cvlc.kill()
    
    os.popen("pkill -9 rtl_fm")
    os.popen("pkill -9 vlc")
    
    #~ fe = -252000 # calculated difference
    fe = -249500    # works

    #
    # SDR rtl_fm command
    #
        
    command  = "rtl_fm -M fm "

    command += " -f " + str( 153785000 + fe )
    command += " -f " + str( 155880000 + fe )
    command += " -f " + str( 151475000 + fe )
    command += " -f " + str( 155625000 + fe )
    command += " -f " + str( 151452500 + fe )
    command += " -f " + str( 154860000 + fe )
    command += " -f " + str( 154950000 + fe )
    command += " -f " + str( 151100000 + fe )
    command += " -f " + str( 154085000 + fe )
    command += " -f " + str( 151115000 + fe )
    command += " -f " + str( 156165000 + fe )
    command += " -f " + str( 154845000 + fe )
    command += " -f " + str( 151122500 + fe )
    command += " -f " + str( 154650000 + fe )
    command += " -f " + str( 159150000 + fe )
    command += " -f " + str( 155700000 + fe )
    command += " -f " + str( 155130000 + fe )
    command += " -f " + str( 153995000 + fe )
    command += " -f " + str( 152840000 + fe )
    command += " -f " + str( 154890000 + fe )
    command += " -f " + str( 173225000 + fe )
    
    command += " -s 16000 -g 50 -l 205 -t 5 -p 0 -A fast | "
    command += "aplay -r 16000 -f S16_LE "
    command += "&> /dev/null &" 
    
    print command
    
    FNULL       = open(os.devnull, 'w')
    sub_radio   = subprocess.Popen(command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    
    ts          = datetime.datetime.now().strftime("%A %B %d, %Y %I:%M:%S %p")
    jsonStr     = '{ "freqNumber" : "' + str(freqNumber)  + '", "freqText" : "' + str(freqText)  + '", "timestamp" : "' +  str(ts) + '" }'
    socketio.emit('tuneFire', data=jsonStr, broadcast=True)    
    
    resp = jsonify({"freqNumber"    : freqNumber ,
                    "freqText"      : freqText 
    })

    return resp


@app.route('/ajaxAir', methods=['GET', 'POST'])
def tuneAir():
    
    global freqText, freqNumber, sub_radio, sub_cvlc
    
    freqNumber  = "Scan Air Band"
    
    freqText    = "Scan Air Band"
    
    if hasattr(sub_radio, 'pid'):
        sub_radio.kill()

    if hasattr(sub_cvlc, 'pid'):
        sub_cvlc.kill()
    
    os.popen("pkill -9 rtl_fm")
    os.popen("pkill -9 vlc")
    
    #~ fe = -252000    # calculated difference
    fe = -249500    # works

    #
    # SDR rtl_fm command
    #
        
    command  = "rtl_fm -M am -f " + str( 118000000 + fe ) + ":" + str( 137000000 + fe ) + ":25000 -s 16000 -g 50 -l 200 -t 5 -A fast | "
    command += "aplay -r 16000 -f S16_LE "
    command += "&> /dev/null &" 
    
    print command
    
    FNULL       = open(os.devnull, 'w')
    sub_radio   = subprocess.Popen(command, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    
    ts          = datetime.datetime.now().strftime("%A %B %d, %Y %I:%M:%S %p")
    jsonStr     = '{ "freqNumber" : "' + str(freqNumber)  + '", "freqText" : "' + str(freqText)  + '", "timestamp" : "' +  str(ts) + '" }'
    socketio.emit('tuneAir', data=jsonStr, broadcast=True)    
    
    resp = jsonify({"freqNumber"    : freqNumber ,
                    "freqText"      : freqText 
    })

    return resp


@app.route('/ajaxStop', methods=['GET', 'POST'])
def stop():
    
    global freqText, freqNumber, sub_radio, sub_cvlc
    
    freqNumber  = "Stop"
    
    freqText    = "Radio Stopped"

    if hasattr(sub_radio, 'pid'):
        sub_radio.kill()    

    if hasattr(sub_cvlc, 'pid'):
        sub_cvlc.kill()
    
    os.popen("sudo pkill -9 rtl_fm")
    os.popen("pkill -9 vlc")
    
    resp = jsonify({"freqNumber"    : freqNumber ,
                    "freqText"      : freqText 
    })

    return resp
    

@socketio.on('connect')
def on_connect():
    
    global freqText, freqNumber
    
    print 'connected: ' + freqText
    

@socketio.on('disconnect')
def on_disconnect():
    
    global freqText, freqNumber
    
    print 'disconnected: ' + freqText


#
# webserver with sockets
#

if __name__ == '__main__':
    #~ socketio.run(app, host='0.0.0.0', port=80, debug=True)
    socketio.run(app, host='0.0.0.0', port=80, debug=False)
