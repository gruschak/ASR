var app = new Vue({
    el: "#app",
    data: {
        uri: "ws://localhost:2700",
        ws: null,
        socket: null,
        resultText: "",
        status: "BARS Group",
    },

    methods: {

        initSocket() {

            console.log("----- initSocket started");
            this.ws = new WebSocket(this.uri);
            console.log(this.ws);

            this.ws.onopen = function(event) {
                console.log("----- onopen");
                this.status = "<strong>Connected</strong> at " + this.uri;
                console.log(this.status)
            }

            this.ws.onclose = function(event) {
                console.log("----- onclose");
                if (event.wasClean) {
                    this.status = "<strong>Connection was successfully closed</strong>";
                } else {
                    this.status = "<strong>Connection dropped!</strong> " +
                        "(code: " + event.code + ", reason: " + event.reason + ")";
                }
            }

            this.ws.onmessage = function(event) {
                let message = JSON.parse(event.data);
                if (message.text) {
                    this.resultText += message.text + "\n";
                    // resultText.scrollTop = resultText.scrollHeight;
                }
            }

            this.ws.onerror = function(event) {
                console.log("----- onerror");
                this.status = "Error:" + event.message;
            }

            console.log("----- initSocket ended");
        },

        connectToServer() {
            if (!this.ws || [this.ws.CONNECTING, this.ws.OPEN].indexOf(this.ws.readyState) === -1) {
                this.ws = this.initSocket();
                this.resultText = "";
            }
            this.resultText = "Tried to connect";
            this.resultText += this.ws;
        },

        closeConnection() {
            if (this.ws || [this.ws.CLOSING, this.ws.CLOSED].indexOf(this.ws.readyState) === -1) {
                this.ws.close();
            }
            this.resultText = "Tried to disconnect";
        },
    },

    beforeMount() {
        console.log('--- beforeMount started');
        this.ws = this.initSocket();

        console.log(this.ws);
        console.log('--- beforeMount ended');
    },

    mounted() {
        console.log('--- mounted started');
    }


});