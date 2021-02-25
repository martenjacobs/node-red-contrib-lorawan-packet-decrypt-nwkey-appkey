const lora_packet = require("lora-packet");
// test ot payload /
//CPU_Load = 30
//Temperature =23.34

//-----------------
// packet decoding

// decode a packet
const packet = lora_packet.fromWire(Buffer.from("408a1a0126006000014ea7f5b4ca2547e4", "hex"));

// debug: prints out contents
// - contents depend on packet type
// - contents are named based on LoRa spec
console.log("packet.toString()=\n" + packet);

// e.g. retrieve payload elements
console.log("packet MIC=" + packet.MIC.toString("hex"));
console.log("FRMPayload=" + packet.FRMPayload.toString("hex"));

// check MIC
const NwkSKey = Buffer.from("27E87B6710ACC5FB9098F19AE77DC62B", "hex");
console.log("MIC check=" + (lora_packet.verifyMIC(packet, NwkSKey) ? "OK" : "fail"));

// calculate MIC based on contents
console.log("calculated MIC=" + lora_packet.calculateMIC(packet, NwkSKey).toString("hex"));

// decrypt payload
const AppSKey = Buffer.from("B887FD00569BE0746E8020746EFC9BA8", "hex");
console.log("Decrypted (ASCII)='" + lora_packet.decrypt(packet, AppSKey, NwkSKey).toString() + "'");
console.log("Decrypted (hex)='0x" + lora_packet.decrypt(packet, AppSKey, NwkSKey).toString("hex") + "'");

newbytes=Buffer.from(lora_packet.decrypt(packet, AppSKey, NwkSKey).toString("hex"), 'hex')
console.log(newbytes) ///yeah

//decode ...payload
//https://learn.adafruit.com/using-lorawan-and-the-things-network-with-circuitpython?view=all

CPU_Load = (newbytes[0] << 8) | newbytes[1];
oTemperature = (newbytes[2] << 8) | newbytes[1];

console.log("CPU_Load = "+CPU_Load)
console.log("Temperature =" + oTemperature/100)

//-----------------
// packet creation

// create a packet
const constructedPacket = lora_packet.fromFields(
  {
    MType: "Unconfirmed Data Up", // (default)
    DevAddr: Buffer.from("01020304", "hex"), // big-endian
    FCtrl: {
      ADR: false, // default = false
      ACK: true, // default = false
      ADRACKReq: false, // default = false
      FPending: false, // default = false
    },
    FCnt: Buffer.from("0003", "hex"), // can supply a buffer or a number
    payload: "test",
  },
  Buffer.from("ec925802ae430ca77fd3dd73cb2cc588", "hex"), // AppSKey
  Buffer.from("44024241ed4ce9a68c6a8bc055233fd3", "hex") // NwkSKey
);
//console.log("constructedPacket.toString()=\n" + constructedPacket);
//const wireFormatPacket = constructedPacket.getPHYPayload();
//console.log("wireFormatPacket.toString()=\n" + wireFormatPacket.toString("hex"));
