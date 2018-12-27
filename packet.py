import json
import base64
import re

class packet:
    JOIN = 0x00
    UPLINK = 0x40

    def __init__(self, data):
        self.type = None

        if (len(data) < 13):
             return

        self.data = data
        self.protocol_version = int(data[0])
        self.random_token = data[1:3]
        self.identifier = data[3]
        self.gateway_addr = data[4:12].hex()

        self.json = json.loads(data[12:len(self.data)].decode())

        try:
            self.payload = base64.b64decode(self.json["rxpk"][0]["data"])
            self.dev_addr = self.payload[1:5].hex()
            self.payload_size = self.json["rxpk"][0]["size"]
            self.frequency = self.json["rxpk"][0]["freq"]
            self.modulation = self.json["rxpk"][0]["modu"]
            self.snr = self.json["rxpk"][0]["lsnr"]
            self.time = self.json["rxpk"][0]["time"]
            self.channel = self.json["rxpk"][0]["chan"]
            self.dr = self.json["rxpk"][0]["datr"]
            self.rssi = self.json["rxpk"][0]["rssi"]
            self.codr = self.json["rxpk"][0]["codr"].split("/")
            self.deveui = None
        except KeyError:
            return

        dr = re.findall("SF(\d{1,2})BW(\d{3})", self.dr)
        self.SF = dr[0][0]
        self.BW = dr[0][1]

        if (self.payload[0] == packet.JOIN):
            print("join")
            self.type = "JOIN"
            self.deveui = self.payload[9:17].hex()
        elif (self.payload[0] == packet.UPLINK):
            print("uplink")
            self.type = "UPLINK"
