from packet import packet
import threading
import time
import queue
import json
import requests

class ttnmon: #Class for collecting and uploading gateway stats to TTNmon
    def __init__(self, upload_interval=5, url="https://api.ttnmon.meis.space/gateways/ttnmon_forwarder/"):
        self.upload_interval = upload_interval
        self.url = url
        self.packets = queue.Queue()
        self.thread = None
        self.runThread = False

    def add(self, pkt): #Adds a packet for uploading
        #if pkt.type == packet.JOIN or pkt.type == packet.UPLINK:
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
        data = []
        n = 0
        for pkt in packets:

            data.append ({
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
                "SF": pkt.SF,
                "BW": pkt.BW,
                "airtime": pkt.airtime
            })
            n += 1

        print(json.dumps(data))
        requests.post(self.url, json = data)

        return True #Upload failed

pkt1 = packet(b'\x01\xf6\xbf\x00\x00\x04\xa3\x0b\x00#0\xf8{"rxpk":[{"tmst":3998410931,"time":"2018-12-27T18:59:58.099949Z","chan":2,"rfch":1,"freq":868.500000,"stat":1,"modu":"LORA","datr":"SF7BW125","codr":"4/5","lsnr":7.0,"rssi":-27,"size":23,"data":"AAaaANB+1bNwNGoo/v+krjBzhxehjXg="}]}')
pkt2 = packet(b'\x01cj\x00\x00\x04\xa3\x0b\x00#0\xf8{"rxpk":[{"tmst":4003536323,"time":"2018-12-27T19:00:03.225380Z","chan":3,"rfch":0,"freq":867.100000,"stat":1,"modu":"LORA","datr":"SF7BW125","codr":"4/5","lsnr":9.8,"rssi":-27,"size":16,"data":"QJIrASaAAAABmmQNcOwJZA=="}]}')
test = ttnmon()
test.add(pkt1)
test.add(pkt2)
test.startThread()
input("Any KEY")
test.stopThread()
