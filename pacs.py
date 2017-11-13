import parser
import paho.mqtt.client as mqtt
import threading

DEV_EUI = "807B85902000022C"
TOPIC_IBTN = "devices/lora/" + DEV_EUI + "/ibutton"
TOPIC_GPIO = "devices/lora/" + DEV_EUI + "/gpio"
DATABASE = {"650000011E996301"}
BASE_STATION_IP = "192.168.4.254"
OPEN_TIME = 10
INVALID_KEY = -1

TEMPLATE = """{ "data": { "id": 650000011E996301 }, "status": { "devEUI" : "807B85902000022C", "rssi": -43, 
"temperature": 30, "battery": 3350, "date": "2017-10-31T15:04:23.215210Z" }}"""
DATA = """{ "data": { "id": 650000011E996301 }, "status": { "devEUI" : "807B85902000022C", "rssi": -43, 
"temperature": 30, "battery": 3350, "date": "2017-10-31T15:04:23.215210Z" }}"""


class Lock:
    def __init(self):
        self.lock = True
        self.ibtn = mqtt.Client(userdata=self)
        self.ibtn.on_connect = self.on_connect_ibtn
        self.ibtn.on_message = self.on_message_ibtn

    @staticmethod
    def on_connect_ibtn(client, userdata, flags, rc):
        print("Client connected to key topic with result code " + str(rc))
        userdata.client.subscribe(TOPIC_IBTN)

    @staticmethod
    def on_message(self, client, userdata, msg):
        if userdata.lock:
            return

        key = parse_key(msg.payload.decode("utf8"))
        lock = True
        if key in DATABASE:
            print("Access granted to key ", key)
            self.open_lock(client)
            event = threading.Event()
            event.wait(OPEN_TIME)
            self.close_lock(client)
            lock = False
        else:
            print("Access denied to key ", key)
            self.open_lock(client)
            event = threading.Event()
            event.wait(OPEN_TIME)
            self.close_lock(client)
            lock = False

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

    def parse_key(msg):
        key = ""
        try:
            data = json.loads(msg)
            print(data["data"])
            key = data["data"]["id"]
            print(key)
        except Exception as e:
            print(type(e), ":", e)
        return key


if __name__ == "__main__":

    client.loop_forever()
