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
                "EVENT_ALERT_" + RewardNumber + "_REDEEMED"
            ]
        };

        // Send authentication data to ChatBot ws server
        socket.send(JSON.stringify(auth));
    };

    //-------------------------------------------
    //  Websocket Event: OnMessage
    //-------------------------------------------
    socket.onmessage = function (message) {

        // Parse message
        var socketMessage = JSON.parse(message.data);
        console.log(socketMessage);

        if (socketMessage.event === "EVENT_ALERT_" + RewardNumber + "_REDEEMED") {
            var data = JSON.parse(socketMessage.data);

            $("#media").attr("src", data.path);
            $("#text").html(data.text);

            $("#container").css('visibility', 'visible')
                .removeClass("animate__fadeOut")
                .addClass("animate__zoomIn");

            setTimeout(function () {
                $("#container").removeClass("animate__zoomIn")
                    .addClass("animate__fadeOut");
            }, 5000);
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

}
