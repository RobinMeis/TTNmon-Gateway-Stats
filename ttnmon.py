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
        self.version = "0.2-dev"
        self.mailto = mailto

    def add(self, pkt): #Adds a packet for uploading
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
                    print ("Upload failed. We have to restore")
                    for pkt in toUpload:
                        self.packets.put(pkt)
                else:
                    print("Upload success")


            slept += 1

    def upload(self, packets):
        print("Starting upload")
        if len(packets) > 0:
            data = {}
            data["version"] = self.version
            data["mailto"] = self.mailto
            data["pkts"] = []
            for pkt in packets:
                data["pkts"].append (pkt)

            try:
                response = requests.post(self.url, json = data)
            except:
                return False
            else:
                if response.status_code == 200:
                    return True
                else:
                    return False
        else:
            print("Skipping upload, no packets received")
        return True
