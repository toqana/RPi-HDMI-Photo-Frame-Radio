# Raspberry Pi Full HD HDMI Photo Frame Carousel with SDR Radio and Internet Radio

### Description

This is a verified and fully functional engineering software and hardware prototype of a Raspberry Pi 3 Model B+ Full HD (1920x1080) photo frame carousel with both Software Defined Radio ("SDR") and Internet Radio audio. The photo frame carousel and audio play through the HDMI port. The 1920x1080 HDMI signal has been tested on both Full HD (1920x1080) and Ultra HD (3840x2160) Samsung televisions.

As an engineering prototype, there are important and necessary functions that need to be added to make this a finished consumer product, such as security hardening, enhancing the web browser-based control panel to make it more consumer friendly, supporting and testing image formats in addition to .jpg and .tiff, and supporting loading photo image files by insertion of a USB thumb drive in addition to the current method of using a FTP client program (e.g. FileZilla) to load photo image files.

This code is provided free of charge without any warranty, guarantee, or promise for support of any kind. The Python, bash, HTML, CSS, and JavaScript code is original, with some code snippets based on examples from public sources (e.g. SDR, VLC, and SDL2 commands). The Python, bash, HTML, JavaScript, and CSS original code provided in this repository is available for re-use without charge subject to the GNU General Public License version 3 (https://www.gnu.org/licenses/gpl.html). If you use any portion of this repository please credit "OTTStreamingVideo.net". When possible, OTTStreamingVideo.net will endeavor to answer questions posted here on GitHub. You are welcome to contact info@OTTStreamingVideo.net for commercial inquiries.

Please also refer to the Raspbian Operating System software license(s), Python software license(s), Flask software license(s), RTL software license(s), SDL2 software license(s), VLC software license(s), and any and all other applicable software licenses.

The SDR Radio is based on the "NooElec RTL-SDR, FM+DAB, DVB-T USB Stick Set with RTL2832U & R820T" that is available from Amazon for $19.95 (https://www.nooelec.com/store/sdr/sdr-receivers/nesdr-mini-rtl2832-r820t.html).

The RPi runs Raspbian Stretch, and the application is written in Python 2.7. The web browser-based user control panel is implemented using the Python Flask webserver running on port 80, which requires the root user. If you do not wish to run the Python application as root, then please change the Flask webserver port.

The HDMI display (i.e. photos and text) is generated in Python using SDL2 (https://www.libsdl.org/). New photos are loaded into "inFolder" (e.g. via a FTP client such as FileZilla), which are then automatically resized (if required) to a maximum size of 1920x1080 while maintaining the aspect ratio, and then loaded into "displayFolder".

The SDR HDMI audio is generated by piping the SDR binary from the SDR USB dongle to the Pulse Audio "aplay" program (https://www.freedesktop.org/wiki/Software/PulseAudio/). This runs as a Python subprocess that can be terminated when the audio source is changed.

The Internet Radio HDMI audio is generated by using "cvlc" (i.e. the command line VLC program) with the Internet Radio stream URL (https://www.videolan.org/index.html). This runs as a Python subprocess that can be terminated when the audio source is changed.

The Python Flask webserver (http://flask.pocoo.org/) uses AJAX to receive commands from one or more control panel browsers, and websockets to send synchronized information to one or more control panel browsers (e.g. current information such as the control panel URL, audio source in use, date, and time) using socketio.background_task.

### RPi Preparation

If you are new to the Raspberry Pi, please refer to https://www.raspberrypi.org/.

If you do not have a RPi NOOBS microSDHC card, a simple way to install Raspbian Stretch on a microSDHC card is to download "RASPBIAN STRETCH WITH DESKTOP AND RECOMMENDED SOFTWARE" from https://downloads.raspberrypi.org/raspbian_full_latest (verified with "2018-11-13-raspbian-stretch-full.zip") and to use Rufus (https://rufus.ie/en_IE.html) to create a bootable microSDHC image on a Windows 7+ PC. OTTStreamingVideo.net typically uses 32 GB microSDHC cards to allow room for multiple development versions of an application and lots of data.

OTTStreamingVideo.net's development platform is Ubuntu based, so we often use Ubuntu Image Writer (https://askubuntu.com/questions/179437/how-can-i-burn-a-raspberry-pi-image-to-sd-card-from-ubuntu) to create microSDHC cards and Geany (https://www.geany.org/Download/ThirdPartyPackages) for code editing.

When you first power up your RPi with a new Raspbian Stretch image, the following steps may be helpful:

1. Connect the SDR USB dongle, a Full HD (1920x1080) monitor with speakers or TV to the HDMI port, in addition to a USB keyboard and mouse (e.g. Logitech K270 wireless keyboard and mouse).

1. Insert the new microSDHC into the RPi and then apply power. After boot, follow the instructions.

1. Change the password for user "pi" using the desktop Preferences -> Raspberry Pi Configuration tool (https://www.raspberrypi.org/magpi/raspberry-pi-configuration-tool/) or the terminal based "sudo raspi-config" command (https://www.raspberrypi.org/documentation/configuration/raspi-config.md). It may also be convenient to enable SSH in order to use a remote terminal. 

1. Update Raspbian with "sudo apt-get update && sudo apt-get upgrade".

1. Update your RPi firmware with "sudo rpi-update", and then reboot with "sudo reboot".

1. Verify that Python 2.7 is the default version with "python -V".

1. Install packages using:
    ```
    sudo apt-get install rtl-sdr gr-osmosdr gqrx-sdr
    ```
    
1. Add the lines shown below for SDR support with the command "sudo nano /etc/udev/rules.d/99-sdr.rules":
    ```
    # Realtek Semiconductor Corp. RTL2838 DVB-T 
    SUBSYSTEMS=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE:="0666", GROUP="adm", SYMLINK+="rtl_sdr"
    ```
1. Reboot with "sudo reboot".

1. Update and upgrade with "sudo apt-get update && sudo apt-get upgrade".

1. Verify operation of the SDR USB dongle with the commands "lsusb" and "rtl_test" (https://drwxr.org/2017/04/setting-up-rtl-sdr-on-raspberry-pi-3/). See also https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr.

1. Verify operation of the SDR USB dongle with a local FM radio station (replace "104.5M" with the frequency of a FM station in your area):
    ```
    rtl_fm -M wbfm -f 104.5M -s 768K -r 96K -E deemp | aplay -c 2 -r 48000 -f S16_LE
    ```
1. Install the following packages using:
    ```
    sudo apt-get install libsdl2-2.0 libsdl2-dev unclutter libjpeg-dev zlib1g-dev vlc bless python-sdl2 libffi-dev
    ```
1. Reboot with "sudo reboot". Update and upgrade with "sudo apt-get update && sudo apt-get upgrade".

1. Verify that vlc has been installed for user pi with "vlc --version".

1. Since the Python Flask webserver requires root for port 80 (https://stackoverflow.com/questions/51396047/running-flask-on-port-80-in-linux), use "sudo pip install package-name" (this makes the python packages available to all users). If you decide not to use port 80 for the Flask webserver then omit "sudo":
   ```
   sudo pip install Flask flask_socketio eventlet imagesize python-resize-image
   ```
1. Install setuptools, cffi, and gevent. If the installation appears to stall, wait 3 minutes and then verify with the next step.
    ```
    sudo pip install setuptools cffi gevent
    ```
1. If the installation in the prior step appears to stall, wait 3 minutes and then verify with:
    ```
    python
    >>>import gevent
    (if gevent has been installed no error message will appear)
    
    or
    
    sudo pip install gevent
    (if gevent has been installed a message will indicate such)
    ```
    You may need to open a new terminal window on the RPi if the installation of gevent appeared to stall.

1. Reboot with "sudo reboot". Update and upgrade with "sudo apt-get update && sudo apt-get upgrade".

1. Verify git is installed with "git --version". If not, install git with "sudo apt-get install git".

1. Due to a recent change in Raspbian Stretch, confirm if the folder "/home/pi/.config/lxsession" exists with "ls /home/pi/.config/lxsession", and also confirm that the folder "/home/pi/.config/lxsession/LXDE-pi" exists with "ls /home/pi/.config/lxsession/LXDE-pi". If not, make them as shown below:
    ```
    mkdir /home/pi/.config/lxsession
    mkdir /home/pi/.config/lxsession/LXDE-pi

1. In order to remove the cursor from the image carousel screen, run the command "nano /home/pi/.config/lxsession/LXDE-pi/autostart" and change (or insert) the file contents to:

    ```
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

1. Edit vlc to allow execution as root with "sudo bless /usr/bin/vlc". Search for the text string "geteuid" and repalce with the text string "getppid", save file, and exit (https://askubuntu.com/questions/413542/how-to-use-vlc-with-sudo-privileges).

1. Verify that cvlc (i.e. the command line vlc) runs as root with "sudo cvlc --version".

1. Pull the repository from GitHub to your RPi "/home/pi" home directory as user pi:
    ```
    cd ~
    git clone https://github.com/ConferVideo/RPi-HDMI-Photo-Frame-Radio.git
    ```

1. Copy the file "sdr_cron_reboot" to the /etc/cron.d folder with the command:
    
    sudo cp /home/pi/RPi-HDMI-Photo-Frame-Radio/sdr_cron_reboot /etc/cron.d/sdr_cron_reboot

1. Test the application with the command:
    ```
    cd ~/RPi-HDMI-Photo-Frame-Radio
    ./sdr_cron_reboot.sh
    ```
1. You can stop the test by using a remote terminal through the command "ssh pi@xxx.xxx.xxx.xxx" with user=pi and password=ThePasswordYouCreatedAbove (default=raspberry), where xxx.xxx.xxx.xxx is the IP address of your RPi that appears on the upper left of the images. You can also obtain your RPi IP address through the "ifconfig" command. To stop the test via SSH use the following commands:
    ```
    sudo pkill -9 sdr # this should kill the image display
    sudo pkill -9 rtl # this should kill the SDR audio
    sudo pkill -9 vlc # this should kill the vlc audio
    sudo pkill -9 python # this should kill any remaining python threads
    ```
1. Test the application from reboot (or power om) with "sudo reboot".

1. To pull an updated copy of this repository, use the following commands:
    ```
    cd ~/RPi-HDMI-Photo-Frame-Radio
    git pull
    ```
