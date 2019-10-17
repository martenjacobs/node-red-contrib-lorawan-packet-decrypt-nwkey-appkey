"""
Example for using the RFM9x Radio with Raspberry Pi and LoRaWAN

Learn Guide: https://learn.adafruit.com/lora-and-lorawan-for-raspberry-pi

some modification see temperature

"""
import threading
import time
import subprocess
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import thte SSD1306 module.
import adafruit_ssd1306
# Import Adafruit TinyLoRa
from adafruit_tinylora.adafruit_tinylora import TTN, TinyLoRa
#outdoor temp
from w1thermsensor import W1ThermSensor
temperature=0
try:
	sensor = W1ThermSensor()
#node there maybe multiple we only read the 1st
	temperature = sensor.get_temperature()
	print("The temperature is %s celsius" % temperature)
	print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))
#    print(sensor)
#    for sensor in W1ThermSensor.get_available_sensors():
#        print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))
#    print("...")
except Exception as e:
	print(e)
	print("Can not read outdoor temp sensor")

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# TinyLoRa Configuration
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.CE1)
irq = DigitalInOut(board.D22)
rst = DigitalInOut(board.D25)

# TTN Device Address, 4 Bytes, MSB
devaddr = bytearray([  0x26, 0x01, 0x1A, 0x8A  ])
# 0x26, 0x01, 0x19, 0xF6 
# TTN Network Key, 16 Bytes, MSB
nwkey = bytearray([ 0x27, 0xE8, 0x7B, 0x67, 0x10, 0xAC, 0xC5, 0xFB, 0x90, 0x98, 0xF1, 0x9A, 0xE7, 0x7D, 0xC6, 0x2B ]) 
#0x2B to 0x2A

#{ 0x60, 0xA2, 0xF0, 0xBE, 0x92, 0xED, 0x2D, 0x86, 0x2D, 0xAF, 0x08, 0xFB, 0x37, 0xEC, 0x92, 0x49 }
# TTN Application Key, 16 Bytess, MSB
app = bytearray([ 0xB8, 0x87, 0xFD, 0x00, 0x56, 0x9B, 0xE0, 0x74, 0x6E, 0x80, 0x20, 0x74, 0x6E, 0xFC, 0x9B, 0xA8 ])
#
#{ 0xE9, 0x62, 0x97, 0x7F, 0x76, 0x20, 0x1A, 0x09, 0x57, 0x39, 0x52, 0x16, 0xF7, 0x6F, 0xE6, 0x45 }

# Initialize ThingsNetwork configuration
ttn_config = TTN(devaddr, nwkey, app, country='US')
#fre 903.9
# Initialize lora object
lora = TinyLoRa(spi, cs, irq, rst, ttn_config)
#lora.set_channel(0)
# 2b array to store sensor data
data_pkt = bytearray(4)
# time to delay periodic packet sends (in seconds)
data_pkt_delay = 10.0

print("LoraWAN Test")

def send_pi_data_periodic():
    threading.Timer(data_pkt_delay, send_pi_data_periodic).start()
    print("Sending periodic data...")
    send_pi_data(CPU)
    print('CPU:', CPU)
#    print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))

def send_pi_data(data):
    global sensor
    # Encode float as int
    data = int(data * 100)
    # Encode payload as bytes
    data_pkt[0] = (data >> 8) & 0xff
    data_pkt[1] = data & 0xff
    # temperature
    try:
        ot = int(sensor.get_temperature() * 100)
    except Exception as e:
        ot=0
    data_pkt[2] = (ot >> 8) & 0xff
    data_pkt[3] = ot & 0xff

    print("otemp = "+str(ot)+" CPU="+str(data))
    # Send data packet
    lora.send_data(data_pkt, len(data_pkt), lora.frame_counter)
    lora.frame_counter += 1
    display.fill(0)
    display.text('Sent Data to TTN!', 15, 15, 1)
    print('Data sent!')
    display.show()
    time.sleep(1)

while True:
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text('RasPi LoRaWAN', 35, 0, 1)

    # read the raspberry pi cpu load
    cmd = "top -bn1 | grep load | awk '{printf \"%.1f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    CPU = float(CPU)
    send_pi_data(CPU)
#    send_pi_data_periodic()
    if not btnA.value:
        # Send Packet
        send_pi_data(CPU)
    if not btnB.value:
        # Display CPU Load
        display.fill(0)
        display.text('CPU Load %', 45, 0, 1)
        display.text(str(CPU), 60, 15, 1)
        display.show()
        time.sleep(0.1)
    if not btnC.value:
        display.fill(0)
        display.text('* Periodic Mode *', 15, 0, 1)
        display.show()
        time.sleep(0.5)
        send_pi_data_periodic()


    display.show()
    time.sleep(5)

