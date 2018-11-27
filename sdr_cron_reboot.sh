#!/bin/bash
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
# emulate RPi Desktop for cron
#
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/usr/local/games:/usr/games
XDG_RUNTIME_DIR=/run/user/1000
export DISPLAY=:0.0
export XAUTHORITY=~/.Xauthority
cd /home/pi/RPi-HDMI-Photo-Frame-Radio
sudo ./sdr.py &
#
# if desired, suppress output
#
#sudo ./sdr.py  >/dev/null 2>&1 &
