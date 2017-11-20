import parser
import paho.mqtt.client as mqtt
import json
import threading

DEV_EUI = "807B85902000022C"
TOPIC_PWM = "devices/lora/" + DEV_EUI + "/pwm"
TOPIC_OPT = "devices/lora/" + DEV_EUI + "/opt3001"
BASE_STATION_IP = "192.168.4.254"
TEMPLATE_OPT = """devices/lora/NNNNNNNNNNNNNNN/opt3001
{
    "data": {
        "Address": SERIAL,
        "luminocity": 32
    },
    "status": {
        "devEUI" : "NNNNNNNNNNNNNNN",
        "rssi" : -16, 
        "temperature" : 30, 
        "battery" : 3300, 
        "date" : "2017-02-21T13:29:22.843900Z"
    }
}"""
COEFF = 1 / 970


class Regulator:
    def __init__(self):
        self.opt = mqtt.Client(userdata=self)
        self.opt.on_connect = self.on_connect
        self.opt.on_message = self.on_message
        self.opt.connect(BASE_STATION_IP)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        print("Client connected to key topic with result code " + str(rc))
        userdata.opt.subscribe(TOPIC_OPT)

    @staticmethod
    def on_message(client, userdata, msg):
        try:
            data = parser.safe_parse(msg.payload.decode("utf8"), TEMPLATE_OPT)
            luminocity = data["data"]["luminocity"]
            if not isinstance(luminocity, float):
                raise TypeError("Luminocity should be of type 'float'")
        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            print(e)

        userdata.opt.publish(TOPIC_PWM, "set freq 970 dev 01 on ch 01 duty " +
                             str((1 - min(luminocity * COEFF, 1) * 100)

if __name__ == "__main__":
    reg = Regulator()
    reg.opt.loop_start()
    while True:
        pass
