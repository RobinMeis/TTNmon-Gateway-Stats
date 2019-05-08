import json
import base64
import re
import math
import codecs

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
        self.gateway_addr = self.ByteToHex(data[4:12])
        self.gateway_id = "eui-%s" % (self.gateway_addr,)
        self.airtime = None

        self.json = json.loads(data[12:len(self.data)].decode())

        try:
            self.payload = base64.b64decode(self.json["rxpk"][0]["data"])
            self.dev_addr = self.ByteToHex(self.reverseBytes(self.payload[1:5]))
            self.payload_size = self.json["rxpk"][0]["size"]
            self.frequency = self.json["rxpk"][0]["freq"]
            self.modulation = self.json["rxpk"][0]["modu"]
            self.snr = self.json["rxpk"][0]["lsnr"]
            self.time = self.json["rxpk"][0]["time"]
            self.channel = self.json["rxpk"][0]["chan"]
            self.dr = self.json["rxpk"][0]["datr"]
            self.rssi = self.json["rxpk"][0]["rssi"]
            self.codr = self.json["rxpk"][0]["codr"].split("/")
            self.cr_k = int(self.codr[0])
            self.cr_n = int(self.codr[1])
            self.fcount = int.from_bytes(self.payload[6:8], byteorder='little')
            self.fcrtl = int.from_bytes(self.payload[5:6], byteorder='big')
            self.adr = bool(self.fcrtl & 0x80)
            self.ack = bool(self.fcrtl & 0x20)
            self.fport = int.from_bytes(self.payload[8:9], byteorder='big')
            self.deveui = None
        except KeyError:
            return

        dr = re.findall("SF(\d{1,2})BW(\d{3})", self.dr)
        self.SF = int(dr[0][0])
        self.BW = int(dr[0][1])
        self.calcAirtime()
        if (self.payload[0] == packet.JOIN):
            self.type = "JOIN"
            self.deveui = self.ByteToHex(self.reverseBytes(self.payload[9:17]))
        elif (self.payload[0] == packet.UPLINK):
            self.type = "UPLINK"

    def ByteToHex(self, byte): #Legacy for Python3.3 support
        return codecs.getencoder('hex')(byte)[0]

    def calcAirtime(self):
        tsym = (pow(2,self.SF) / (self.BW * 1000)) * 1000
        tpreamble = (8 + 4.25) * tsym
        payloadSymNb = 8+(max(math.ceil((8*self.payload_size-4*self.SF+28+16-20*(1-1))/(4*(self.SF-2*0)))*(self.cr_n),0))
        tpayload = payloadSymNb * tsym
        tpacket = tpayload + tpreamble
        self.airtime = tpacket

    def reverseBytes(self, toReverse):
        array = bytearray(toReverse)
        array.reverse()
        return bytes(array)
