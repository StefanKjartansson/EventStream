(function () {
    "use strict";

    var updater = {
        socket: null,
        start: function() {
            var url = "ws://" + location.host + "/msgs";
            updater.socket = ("WebSocket" in window) ? (new WebSocket(url)) : (new MozWebSocket(url));
            updater.socket.onmessage = function(event) {
                updater.showMessage(JSON.parse(event.data));
            };
        },
        showMessage: function(message) {
            var node = $(message.html);
            node.find('time.timeago').timeago();
            $("#inbox").prepend(node);
        }
    };

    $(function(){
        if (!window.console) window.console = {};
        if (!window.console.log) window.console.log = function() {};
        updater.start();
        $("time.timeago").timeago();
    });

}).call(this);
