from packet import packet
import threading
import time
import queue
import requests

class ttnmon: #Class for collecting and uploading gateway stats to TTNmon
    def __init__(self, mailto, upload_interval=60, url="https://api.ttnmon.meis.space/gateways/ttnmon_forwarder/"):
        self.upload_interval = upload_interval
        self.url = url
        self.packets = queue.Queue()
        self.thread = None
        self.runThread = False
        self.version = "0.1"
        self.mailto = mailto

    def add(self, pkt): #Adds a packet for uploading
        if pkt.type == "JOIN" or pkt.type == "UPLINK":
            self.packets.put(pkt)

    def startThread(self): #Start the background task
        self.runThread = True
        self.thread = threading.Thread(target=self.__thread)
        self.thread.start()

    def stopThread(self): #Stops the background task
        self.runThread = False
        self.thread.join()

    def __thread(self): #Wait until it's time for uploading
        slept = 0
        while self.runThread:
            time.sleep(1)
            if (slept >= self.upload_interval):
                slept = 0
                toUpload = []
                while (not self.packets.empty()): #Collect packets for upload
                    toUpload.append(self.packets.get())

                if (self.upload(toUpload) == False): #Try upload, if fails restore packets
                    print ("we have to restore")
                    for pkt in toUpload:
                        self.packets.put(pkt)


            slept += 1

    def upload(self, packets):
        if len(packets) > 0:
            data = {}
            data["version"] = self.version
            data["mailto"] = self.mailto
            data["pkts"] = []
            for pkt in packets:
                data["pkts"].append ({
                    "type": pkt.type,
                    "dev_addr": pkt.dev_addr,
                    "payload_size": pkt.payload_size,
                    "frequency": pkt.frequency,
                    "modulation": pkt.modulation,
                    "snr": pkt.snr,
                    "time": pkt.time,
                    "channel": pkt.channel,
                    "rssi": pkt.rssi,
                    "deveui": pkt.deveui,
                    "cr_k": pkt.cr_k,
                    "cr_n": pkt.cr_n,
                    "adr": pkt.adr,
                    "ack": pkt.ack,
                    "SF": pkt.SF,
                    "BW": pkt.BW,
                    "fport": pkt.fport,
                    "airtime": pkt.airtime,
                    "gtw_addr": pkt.gateway_addr,
                    "gtw_id": pkt.gateway_id,
                    "fcount": pkt.fcount
                })

            try:
                response = requests.post(self.url, json = data)
            except:
                return False
            else:
                if response.status_code == 200:
                    return True
                else:
                    return False
        return True
