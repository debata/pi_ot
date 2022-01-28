import time
import sys, os
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

#Setup GPIO
GPIO.setmode(GPIO.BCM)

DOOR_PIN=2
RELAY_PIN=21
BROKER_ADDRESS="192.168.2.244"
GARAGE_TRIGGER_TOPIC="pi/garage_opener/trigger"
# Door sensor
GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Door relay
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)

# Setup MQTT client
def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe(GARAGE_TRIGGER_TOPIC)  #

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    
    decoded_msg=str(msg.payload.decode("utf-8"))
                    
    print("Message received-> " +decoded_msg)  # Print a received msg
    if decoded_msg == "ACTIVE":
        print("GO")
        GPIO.output(RELAY_PIN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(RELAY_PIN, GPIO.HIGH)

def main(): 
    print("creating new instance")
    client = mqtt.Client("Garage") #create new instance
    client.subscribe(GARAGE_TRIGGER_TOPIC)
    client.on_connect=on_connect
    client.on_message=on_message #attach function to callback
    print("connecting to broker")
    client.connect(BROKER_ADDRESS,1883) #connect to broker
    client.loop_start() #start the loop
    
    # Setup MQTT HA sensors
    
    # Garage Door Sensor
    base_topic_door="homeassistant/binary_sensor/garage_door/"
    config_topic_door=base_topic_door + "config"
    state_topic_door=base_topic_door + "state"
    print("Publishing config message to topics")
    payload='{"name": "garage_door", "device_class": "garage_door", "state_topic": "'+state_topic_door+'"}'
    print(payload)
    client.publish(config_topic_door,payload,qos=1)
    while True:
        try:
            # Check door sensor
            state=""
            if GPIO.input(DOOR_PIN):
                print("Door is open")
                state="ON"
                
            elif GPIO.input(DOOR_PIN) == False:
                print("Door is closed")
                state="OFF"
            client.publish(state_topic_door, state)
            
        except Exception as error:
            client.loop_stop() #stop the loop
            client.disconnect()
            GPIO.cleanup(RELAY_PIN, DOOR_PIN)
            raise error
        
        time.sleep(1.0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup(RELAY_PIN, DOOR_PIN)
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)