// Start ws connection after document is loaded
$(document).ready(function () {

    // Connect if API_Key is inserted
    // Else show an error on the overlay
    if (typeof API_Key === "undefined") {
        $("body").html("No API Key found or load!<br>Right click on the script in ChatBot and select \"Insert API Key\"");
        $("body").css({ "font-size": "20px", "color": "#ff8080", "text-align": "center" });
    }
    else {
        connectWebsocket();
    }

});

$("#header").fitText().fitText(1.2);;
$("#time").fitText().fitText(0.5);;

// Connect to ChatBot websocket
// Automatically tries to reconnect on
// disconnection by recalling this method
function connectWebsocket() {

    //-------------------------------------------
    //  Create WebSocket
    //-------------------------------------------
    var socket = new WebSocket(API_Socket);

    //-------------------------------------------
    //  Websocket Event: OnOpen
    //-------------------------------------------
    socket.onopen = function () {

        // AnkhBot Authentication Information
        var auth = {
            author: "EncryptedThoughts",
            website: "twitch.tv/encryptedthoughts",
            api_key: API_Key,
            events: [
                "EVENT_NO_FUDGES_REDEEMED",
                "EVENT_FUCKED_UP"
            ]
        };

        // Send authentication data to ChatBot ws server
        socket.send(JSON.stringify(auth));
    };

    //-------------------------------------------
    //  Websocket Event: OnMessage
    //-------------------------------------------
    socket.onmessage = function (message) {

        var socketMessage = JSON.parse(message.data);
        console.log(socketMessage);

        if (socketMessage.event === "EVENT_NO_FUDGES_REDEEMED") {

            data = JSON.parse(socketMessage.data);
            PlaySound(data.redeemedSFXPath, data.redeemedSFXVolume)
            if (timer > 0)
                timer += data.seconds;
            else {
                var minutes = parseInt(data.seconds / 60, 10);
                var seconds = parseInt(data.seconds % 60, 10);
                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;
                $('#time').text(minutes + ":" + seconds);
                StartTimer(data.seconds - 1, $('#time'), data.finishedSFXPath, data.finishedSFXVolume);
                $("body").css('visibility', 'visible');
                $("body").removeClass("animate__zoomOut");
                $("body").addClass("animate__zoomIn");
            }
        }
        else if (socketMessage.event === "EVENT_FUCKED_UP") {
            data = JSON.parse(socketMessage.data);
            if (timer <= 0) {
                PlaySound(data.redeemedSFXPath, data.redeemedSFXVolume)
                var minutes = parseInt(data.interval / 60, 10);
                var seconds = parseInt(data.interval % 60, 10);
                minutes = minutes < 10 ? "0" + minutes : minutes;
                seconds = seconds < 10 ? "0" + seconds : seconds;
                $('#time').text(minutes + ":" + seconds);
                StartTimer(data.interval - 1, $('#time'), data.finishedSFXPath, data.finishedSFXVolume);
                $("body").css('visibility', 'visible');
                $("body").removeClass("animate__zoomOut");
                $("body").addClass("animate__zoomIn");
            }
            else if (data.type === "reset")
                timer = timer - (timer % data.interval) + data.interval;
            else
                timer += data.interval
        }
    };

    //-------------------------------------------
    //  Websocket Event: OnError
    //-------------------------------------------
    socket.onerror = function (error) {
        console.log("Error: " + error);
    };

    //-------------------------------------------
    //  Websocket Event: OnClose
    //-------------------------------------------
    socket.onclose = function () {
        // Clear socket to avoid multiple ws objects and EventHandlings
        socket = null;
        // Try to reconnect every 5s
        setTimeout(function () { connectWebsocket() }, 5000);
    };

    var timer = 0
    StartTimer = function (duration, display, path, volume) {
        timer = duration;
        var minutes = parseInt(timer / 60, 10);
        var seconds = parseInt(timer % 60, 10);
        var interval = setInterval(function () {
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            display.text(minutes + ":" + seconds);

            if (timer > 0)
                timer--;
            else {
                timer = 0;
                display.text("00:00");
                clearInterval(interval)
                $("body").removeClass("animate__zoomIn")
                $("body").addClass("animate__zoomOut")
                PlaySound(path, volume)
            }
        }, 1000);
    }

    PlaySound = function (path, volume) {
        var audio = new Audio(path);
        audio.volume = volume;
        audio.loop = false;
        audio.play();
    }

}
