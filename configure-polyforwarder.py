import json

#Read current configuration
with open("/opt/ttn-gateway/bin/local_conf.json", 'r') as file:
    config = json.loads(file.read())
    servers = config["gateway_conf"]["servers"]

#Check if TTNmon is already configured
found_server = False
for server in servers:
    if ((server["server_address"] == "127.0.0.1" or server["server_address"] == "localhost") and server["serv_port_up"] == 1700 and server["serv_enabled"] == True):
        found_server = True

#Add TTNmon to configuration
if (not found_server):
    config["gateway_conf"]["servers"].append({ "server_address": "127.0.0.1", "serv_port_up": 1700, "serv_port_down": 1700, "serv_enabled": True})

#Generate NICE JSON from new config
config = json.dumps(config, indent=4, sort_keys=True)

#And write the config file
with open("/opt/ttn-gateway/bin/local_conf.json", 'w') as file:
    file.write(config)
