# Raspberry Pi Full HD HDMI Photo Frame Carousel with SDR Radio and Internet Radio

### Description

This is a verified and fully functional engineering software and hardware prototype of a Raspberry Pi 3 Model B+ Full HD (1920x1080) photo frame carousel with both Software Defined Radio ("SDR") and Internet Radio audio. The photo frame carousel and audio play through the HDMI port. The 1920x1080 HDMI signal has been tested on both Full HD (1920x1080) and Ultra HD (3840x2160) Samsung televisions.

As an engineering prototype, there are important and necessary functions that need to be added to make this a finished consumer product, such as security hardening, enhanced the web browser based control panel to make it more consumer friendly, supporting image formats in addition to .jpg, and supporting loading photo image files by insertion of a USB thumb drive in addition to the current method of using a FTP client program (e.g. FileZilla) to load photo image files.

This code is provided free of charge without any warranty, guarantee, or promise for support of any kind. The Python, HTML, CSS, and JavaScript, code is original, with some code snippets based on examples from public sources (e.g. SDR, VLC, and SDL2 commands). The bash, Python, HTML, JavaScript, and CSS original code provided in this repository is available for re-use without charge subject to the GNU General Public License version 3 (https://www.gnu.org/licenses/gpl.html). If you use any portion of this repository please credit "OTTStreamingVideo.net". When possible, OTTStreamingVideo.net will endeavor to answer questions posted here on GitHub. You are welcome to contact info@OTTStreamingVideo.net for commercial inquiries.

Please also refer to the Raspbian Operating System software license(s), Python software license(s), Flask software license(s), RTL software license(s), SDL2 software license(s), VLC software license(s), and any and all other applicable software licenses.

The SDR Radio is based on the "NooElec RTL-SDR, FM+DAB, DVB-T USB Stick Set with RTL2832U & R820T" that is available from Amazon for $19.95 (https://www.nooelec.com/store/sdr/sdr-receivers/nesdr-mini-rtl2832-r820t.html).

The RPi runs Raspbian Stretch, and the application is written in Python 2.7. The web browser based user control panel is implemented using the Python Flask webserver running on port 80, which requires the root user. If you do not wish to run the Python application as root, then please change the Flask webserver port.

The HDMI display (i.e. photos and text) is generated in Python using SDL2 (https://www.libsdl.org/). New photos are loaded into "inFolder", which are then automatically resized to an aspect ratio correct maximum size of 1920x1080 (if required), and then loaded into "displayFolder".

The SDR HDMI audio is generated by piping the SDR binary to the Pulse Audio "aplay" program (https://www.freedesktop.org/wiki/Software/PulseAudio/). This runs as a Python subprocess that can be terminated when the audio source is changed.

The Internet Radio HDMI audio is generated by using "cvlc" (i.e. the command line VLC program) with the Internet Radio stream URL (https://www.videolan.org/index.html). This runs as a Python subprocess that can be terminated when the audio source is changed.

The Python Flask webserver (http://flask.pocoo.org/) uses AJAX to receive commands from one or more control panel browsers, and websockets to send synchronized information to one or more control panel browsers (e.g. the control panel URL, audio source in use, date, and time) using socketio.background_task.

### RPi Preparation

If you are new to the Raspberry Pi, please refer to https://www.raspberrypi.org/.

If you do not have a RPi NOOBS microSDHC card, a simple way to install Raspbian Stretch on a microSDHC card is to download "RASPBIAN STRETCH WITH DESKTOP AND RECOMMENDED SOFTWARE" from https://downloads.raspberrypi.org/raspbian_full_latest and to use Rufus (https://rufus.ie/en_IE.html) to create a bootable microSDHC image on a Windows 7+ PC. OTTStreamingVideo.net typically uses 32 GB microSDHC cards to allow room for multiple development versions of an application and lots of data.

OTTStreamingVideo.net's developmemt platform is Ubuntu based, so we often use Ubuntu Image Writer (https://askubuntu.com/questions/179437/how-can-i-burn-a-raspberry-pi-image-to-sd-card-from-ubuntu) to create microSDHC cards and Geany (https://www.geany.org/Download/ThirdPartyPackages) for code editing.

When you first power up your RPi with a new Raspbian Stretch image, the following steps may be helpful:

1. Change the password for user "pi" using the desktop Raspberry Pi Configuration Tools (https://www.raspberrypi.org/magpi/raspberry-pi-configuration-tool/) or the terminal based "sudo raspi-config" command (https://www.raspberrypi.org/documentation/configuration/raspi-config.md).

1. Update Raspbian with "sudo apt-get update && sudo apt-get upgrade".

1. Update your RPi firmware with "sudo rpi-update".

1. Verify that Python 2.7 is the default version with "python -V".

1. Verify that pip is installed with version is 18.1 or higher with "pip -V", If not, upgrade pip with "pip install --upgrade pip".

1. Since the Python Flask webserver requires root for port 80 (https://stackoverflow.com/questions/51396047/running-flask-on-port-80-in-linux), it may save time to install python packages with "pip install package-name" and also "sudo pip install package-name". You may also wish to run "sudo pip -V", and, if necessary, 'sudo pip install --upgrade pip". If you decide not to use port 80 then it is not necessary to use "sudo pip install package-name".

1. Install the following packages using "sudo apt-get install package-name":
    ```
    libffi-dev
    rtl-sdr
    libsdl2-2.0
    libsdl2-dev
    unclutter
    libjpeg-div
    zlib1g-dev
    vlc
    bless
    ```

1. Reboot with "sudo reboot". Update and upgrade with "sudo apt-get update && sudo apt-get upgrade".

1. Install the following packages using both "pip install package-name" and "sudo pip install package-name":
    ```
    Flask
    gevent
    flask_socketio
    eventlet
    python-sdl2
    imagesize
    python-resize-image
    ```

1. Reboot with "sudo reboot". Update and upgrade with "sudo apt-get update && sudo apt-get upgrade".

1. Add the lines shown below for SDR support with the command "sudo nano 99-sdr.rules":
    ```
    \# Realtek Semiconductor Corp. RTL2838 DVB-T 
    SUBSYSTEMS=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE:="0666", GROUP="adm", SYMLINK+="rtl_sdr"
    ```

1. Reboot with "sudo reboot".

1. Verify operation of the SDR USB dongle with the commands "lsusb" and "rtl_test" (https://drwxr.org/2017/04/setting-up-rtl-sdr-on-raspberry-pi-3/). See also https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr.

1. Verify git is installed with "git --version". If not, install git with "sudo apt-get install git".

1. Edit /home/pi/.config/lxsession/LXDE-pi/autostart to remove the cursor from the screen with the command:

    nano /home/pi/.config/lxsession/LXDE-pi/autostart

    ```
    from:
    
    @lxpanel --profile LXDE-pi
    @pcmanfm --desktop --profile LXDE-pi
    @xscreensaver -no-splash
    @point-rpi
    
    to:
    
    @lxpanel --profile LXDE-pi
    @pcmanfm --desktop --profile LXDE-pi
    @xscreensaver -no-splash
    @point-rpi
    #
    # for carousel and kiosk, move cursor to center and hide       
    #
    # sudo apt-get install unclutter
    #
    @unclutter -idle 0.1 -root
    ```

1. Edit vlc to allow execution as root with "sudo bless /usr/bin/vlc". Search for the text string "geteuid" and repalce with the text string "getppid:, save file, and exit (https://askubuntu.com/questions/413542/how-to-use-vlc-with-sudo-privileges).

1. Pull the repository from GitHub to your RPi "/home/pi" home directory as user pi:
    ```
    cd ~
    git clone https://github.com/ConferVideo/RPi-HDMI-Photo-Frame-Radio.git
    git pull
    ```

1. Copy the file "sdr_cron_reboot" to the /etc/cron.d folder with the command:
    
    sudo cp /home/pi/sdr/sdr_cron_reboot /etc/cron.d/sdr_cron_reboot

1. Test the application with the command:

    cd ~/sdr
    ./sdr_cron_reboot.sh

1. Next step:


