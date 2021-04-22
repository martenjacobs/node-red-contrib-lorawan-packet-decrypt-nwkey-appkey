// mvk@ca.ibm.com
// adjustments
// 2021-Mar-21
module.exports = function(RED) {

    var lora_packet = require('lora-packet');
    
    function lorawandecrypt(config) {
        RED.nodes.createNode(this, config);
        var node = this;

        node.on('input', function(msg) {
            if(msg.payload.length>1){


                if(msg.payload !== undefined){
                    var indata = msg.payload
                    var packet = lora_packet.fromWire(new Buffer(msg.payload, 'base64'));
                    msg.payload={}
                    msg.payload.in = indata   
                    var NwkSKey = new Buffer(msg.nsw || config.nsw, 'hex');
                    if(lora_packet.verifyMIC(packet, NwkSKey)){
                        var AppSKey = new Buffer(msg.asw || config.asw, 'hex');
                        msg.payload.out = lora_packet.decrypt(packet, AppSKey, NwkSKey).toString('hex');
                        msg.payload.buffers = packet.getBuffers();
                        node.status({});
                        node.send(msg);

                    } else {
                        this.error("Network Key issue! Raw packet: " + packet );
                        node.send(null);
                    }
                } else {
                    node.send(null);
                }
            } else {
                node.send(null);
            }

        });

        node.on("close", function() {
        });
    }

    RED.nodes.registerType("lorawan-packet-decrypt-nwkey-appkey", lorawandecrypt);
};
