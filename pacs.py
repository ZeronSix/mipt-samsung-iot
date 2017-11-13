import parser
import paho.mqtt.client as mqtt
import json
import threading

DEV_EUI = "807B85902000022C"
TOPIC_IBTN = "devices/lora/" + DEV_EUI + "/ibutton"
TOPIC_GPIO = "devices/lora/" + DEV_EUI + "/gpio"
DATABASE = set()
BASE_STATION_IP = "192.168.4.254"
OPEN_TIME = 10
INVALID_KEY = -1

TEMPLATE = """{ "data": { "id": "" }, "status": { "devEUI" : "807B85902000022C", "rssi": -43, 
"temperature": 30, "battery": 3350, "date": "2017-10-31T15:04:23.215210Z" }}"""
TEMPLATE2 = """{ "data": { "msg": "set ok" }, "status": { "devEUI" : "807B85902000022C", "rssi": -60, "temperature": 30, "battery": 3350, "date": "2017-10-31T15:18:37.576462Z" }}"""


class Lock:
    def __init__(self):
        self.lock = False
        self.ibtn = mqtt.Client(userdata=self)
        self.ibtn.on_connect = self.on_connect_ibtn
        self.ibtn.on_message = self.on_message_ibtn
        self.ibtn.connect(BASE_STATION_IP)

    @staticmethod
    def on_connect_ibtn(client, userdata, flags, rc):
        print("Client connected to key topic with result code " + str(rc))
        userdata.ibtn.subscribe(TOPIC_IBTN)

    @staticmethod
    def on_message_ibtn(client, userdata, msg):
        key = Lock.parse_key(msg.payload.decode("utf8"))
        if not key:
            return

        if key in DATABASE:
            print("Access granted to key ", key)
            Lock.open_lock(client)
            event = threading.Event()
            event.wait(OPEN_TIME)
            Lock.close_lock(client)
        else:
            if len(DATABASE) == 0:
                print("Added key", key)
                DATABASE.add(key)
                return
            print("Access denied to key ", key)
            Lock.deny_access(client)
            event = threading.Event()
            event.wait(OPEN_TIME)
            Lock.disable_led(client)

    @staticmethod
    def set_red(client, value):
        client.publish(TOPIC_GPIO, "set 17 " + str(value))

    @staticmethod
    def set_green(client, value):
        client.publish(TOPIC_GPIO, "set 16 " + str(value))

    @staticmethod
    def open_lock(client):
        print("Lock has been opened")
        Lock.set_red(client, 0)
        Lock.set_green(client, 1)

    @staticmethod
    def close_lock(client):
        print("Lock has been closed")
        Lock.set_red(client, 0)
        Lock.set_green(client, 0)

    @staticmethod
    def deny_access(client):
        Lock.set_red(client, 1)
        Lock.set_green(client, 0)

    @staticmethod
    def disable_led(client):
        Lock.set_red(client, 0)
        Lock.set_green(client, 0)

    @staticmethod
    def parse_key(msg):
        key = ""
        try:
            data = parser.safe_parse(msg, TEMPLATE)
            key = data["data"]["id"]
            if not isinstance(key, str):
                raise TypeError("Key should be of type 'str'")
        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            print(e)
        return key


if __name__ == "__main__":
    lock = Lock()
    lock.ibtn.loop_start()
    while True:
        pass
