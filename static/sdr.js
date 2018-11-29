/*

Raspberry Pi Full HD HDMI Photo Frame Carousel with SDR Radio and Internet Radio
Copyright (C) 2018  OTTStreamingVideo.net, Toqana Consulting, LLC (A Nevada Limited Liability Company)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

*/

//
// clf = console log flag
//
// cl  = console log function
//

var clf = true;

Object.defineProperty(Date.prototype, 'YYYYMMDDHHMMSSmmm', {
    
    value: function() {
		
        function pad2(n) {  // always returns a string
            return (n < 10 ? '00' : '') + n;
        }

        function pad3(n) {  // always returns a string
            return (n < 100 ? '0' : '') + n;
        }
        
        return this.getFullYear() + '-' +
               pad2(this.getMonth() + 1) + '-' +
               pad2(this.getDate()) + '_' +
               pad2(this.getHours()) + ':' +
               pad2(this.getMinutes()) + ':' +
               pad2(this.getSeconds()) + '.' +
               pad3(this.getMilliseconds());
    }
});


function cl(msg){
	
	if(clf){
		console.log(new Date().YYYYMMDDHHMMSSmmm() + ' : ' + msg);
	}
	
}


function ajaxChannel(newChannel, newFreq){
    
    cl('ajaxChannel newChannel: ' + newChannel + ', newFreq: ' + newFreq);
    
    var xhr = new XMLHttpRequest();
    var url = "/ajaxChannel";
    
    xhr.open("POST", url, true); // true is for async
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ "newChannel": newChannel, "newFreq" : newFreq }));
    
    xhr.onreadystatechange = function() {
        
        if(xhr.readyState == 4){
            
            cl('ajaxFM() xhr.readyState == 4');
            cl(xhr.responseText);

        }
        
    };

}


function ajaxFM(newFreq){
    
    cl('ajaxFM(' + newFreq + ')');
    
    var xhr = new XMLHttpRequest();
    var url = "/ajaxFM";
    
    xhr.open("POST", url, true); // true is for async
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ "newFreq": newFreq }));
    
    xhr.onreadystatechange = function() {
        
        if(xhr.readyState == 4){
            
            cl('ajaxFM() xhr.readyState == 4');
            cl(xhr.responseText);

        }
        
    };

}

function ajaxFire(){
    
    cl('ajaxFire()');
    
    if( document.getElementById('video_0') != null ){ videoPlayer.dispose(); }
    
    var xhr = new XMLHttpRequest();
    var url = "/ajaxFire";
    
    xhr.open("POST", url, true); // true is for async
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ "newFreq": "Scan Fire Band" }));
    
    xhr.onreadystatechange = function() {
        
        if(xhr.readyState == 4){
            
            cl('ajaxFire() xhr.readyState == 4');
            cl(xhr.responseText);
                
            // RPi play only, audio may not be available to create m3u8 files
            
        }
        
    };

}

function ajaxAir(){
    
    cl('ajaxAir()');
    
    if( document.getElementById('video_0') != null ){ videoPlayer.dispose(); } 
    
    var xhr = new XMLHttpRequest();
    var url = "/ajaxAir";
    
    xhr.open("POST", url, true); // true is for async
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ "newFreq": "Scan Air Band" }));
    
    xhr.onreadystatechange = function() {
        
        if(xhr.readyState == 4){
            
            cl('ajaxAir() xhr.readyState == 4');
            cl(xhr.responseText);            
                
            // RPi play only, audio may not be available to create m3u8 files

        }
        
    };

}

function ajaxStop(){
    
    cl('ajaxStop()');
    
    var xhr = new XMLHttpRequest();
    var url = "/ajaxStop";
    
    xhr.open("POST", url, true); // true is for async
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ "newFreq": "Stop" }));
    
    xhr.onreadystatechange = function() {
        
        if(xhr.readyState == 4){

            cl('ajaxStop() xhr.readyState == 4');
            cl(xhr.responseText);
                        
            var respJSON = JSON.parse(xhr.responseText);
            
            document.getElementById('sockFreq').innerHTML   = respJSON.freqText;
            
        }
        
    };

}

function ajaxLoadImages(){
    
    cl('ajaxLoadImages()');
    
    var xhr = new XMLHttpRequest();
    var url = "/ajaxLoadImages";
    
    xhr.open("POST", url, true); // true is for async
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ "newFreq": "LoadImages" }));
    
    xhr.onreadystatechange = function() {
        
        if(xhr.readyState == 4){

            cl('ajaxLoadImages() xhr.readyState == 4');
            cl(xhr.responseText);
                        
            var respJSON = JSON.parse(xhr.responseText);
            
            document.getElementById('sockFreq').innerHTML   = respJSON.freqText;
            
        }
        
    };

}


function ajaxRestart(){
    
    cl('ajaxRestart()');
    
    var xhr = new XMLHttpRequest();
    var url = "/ajaxRestart";
    
    xhr.open("POST", url, true); // true is for async
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({ "newFreq": "Restart" }));
    
    xhr.onreadystatechange = function() {
        
        if(xhr.readyState == 4){

            cl('ajaxRestart() xhr.readyState == 4');
            cl(xhr.responseText);
                        
            var respJSON = JSON.parse(xhr.responseText);
            
            document.getElementById('sockFreq').innerHTML   = respJSON.freqText;
            
        }
        
    };

}

onload = function(){
    
    var server = 'http://' + document.domain + ':' + location.port;
    cl('onload server: ' + server);
    var socket = io(server);

    // verify our websocket connection is established

    socket.on('connect', function() {
        
        cl('Websocket connected');
    
    });
    
    socket.on('disconnect', function(){
        
         cl('Websocket disconnected');
        
    }); 

    socket.on('freqUpdate', function(data){
        
        var jsonData    = JSON.parse(data);
        //~ cl('freqUpdate: ' + jsonData);
        
        document.getElementById('sockTS').innerHTML     = jsonData.timestamp;
        document.getElementById('sockFreq').innerHTML   = jsonData.freqText;
        
    });

    socket.on('tuneFM', function(data){
        
        var jsonData    = JSON.parse(data);
        cl('socket.on tuneFM jsonData.freqText: ' + jsonData.freqText);
        
        document.getElementById('sockTS').innerHTML     = jsonData.timestamp;
        document.getElementById('sockFreq').innerHTML   = jsonData.freqText;

    });

    socket.on('tuneFire', function(data){
        
        var jsonData    = JSON.parse(data);
        cl('socket.on tuneFire jsonData.freqText: ' + jsonData.freqText);
        
        document.getElementById('sockTS').innerHTML     = jsonData.timestamp;
        document.getElementById('sockFreq').innerHTML   = jsonData.freqText;

    });
    
    socket.on('tuneAir', function(data){
        
        var jsonData    = JSON.parse(data);
        cl('socket.on tuneAir jsonData.freqText: ' + jsonData.freqText);
        
        document.getElementById('sockTS').innerHTML     = jsonData.timestamp;
        document.getElementById('sockFreq').innerHTML   = jsonData.freqText;

    });
        
}

