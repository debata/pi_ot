# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time, os, sys
import board
import adafruit_dht
import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    
BROKER_ADDRESS="192.168.2.244"

def main():

    print("creating new instance")
    client = mqtt.Client("TempSensor") #create new instance
    client.on_message=on_message #attach function to callback
    print("connecting to broker")
    client.connect(BROKER_ADDRESS,1883) #connect to broker
    client.loop_start() #start the loop
    
    # Garage Temperature
    base_topic="homeassistant/sensor/garage/"
    base_topic_temp="homeassistant/sensor/garage_temp/"
    base_topic_humid="homeassistant/sensor/garage_humid/"
    config_topic_temp= base_topic_temp +"config"
    config_topic_humid=base_topic_humid +"config"
    
    payload='{"device_class": "temperature", "name": "garage_temp", "state_topic": "'+base_topic+'state", "unit_of_measurement": "°C", "value_template": "{{ value_json.temperature}}" }'
    client.publish(config_topic_temp,payload)
    print(payload)
    payload='{"device_class": "humidity", "name": "garage_humidity", "state_topic": "'+base_topic+'state", "unit_of_measurement": "%", "value_template": "{{ value_json.humidity}}" }'
    client.publish(config_topic_humid,payload)
    print(payload)
    
    # Initial the dht device, with data pin connected to:
    dhtDevice = adafruit_dht.DHT22(board.D18)
    
    # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
    # This may be necessary on a Linux single board computer like the Raspberry Pi,
    # but it will not work in CircuitPython.
    # dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)
    
    while True:
        try:
            # Read temperature and humidity
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            payload='{ "temperature": '+str(temperature_c)+', "humidity": '+str(humidity)+' }'
            print(payload)
            client.publish(base_topic+'state',payload)
    
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error
    
        time.sleep(30.0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
