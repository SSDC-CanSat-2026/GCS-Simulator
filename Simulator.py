from dataclasses import dataclass
import random
import time
from threading import Thread
from datetime import datetime, timezone
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
import csv


#Initialization
@dataclass
class SimulatorObjects:
    TEAM_ID = 1075
    MISSION_TIME = "XX:XX:XX"
    PACKET_COUNT = 0
    MODE = "F"
    STATE = "LAUNCH_PAD"
    ALTITUDE = 0.0
    TEMPERATURE = 0.0
    PRESSURE = 0.0
    VOLTAGE = 0.0
    CURRENT = 0.0
    GYRO_R = 0.0
    GYRO_P = 0.0
    GYRO_Y = 0.0
    ACCEL_R = 0
    ACCEL_P = 0
    ACCEL_Y = 0
    GPS_TIME = "XX:XX:XX"
    GPS_ALTITUDE = 0.0
    GPS_LATITUDE = 0.0
    GPS_LONGITUDE = 0.0
    GPS_SATS = 0
    CMD_ECHO = "CXON"
    TX_ENABLED = True

   
my_fake_packet = SimulatorObjects()


def randomize():
        my_fake_packet.PACKET_COUNT += 1
        my_fake_packet.MISSION_TIME = datetime.now().strftime("%H:%M:%S")
        utc_now = datetime.now(timezone.utc)
        my_fake_packet.GPS_TIME = utc_now.strftime("%H:%M:%S")

        my_fake_packet.ALTITUDE += 1
        my_fake_packet.TEMPERATURE = round(random.uniform(-10, 40),1)
        my_fake_packet.PRESSURE = round(random.uniform(900, 1100),1)
        my_fake_packet.VOLTAGE = round(random.uniform(7.0, 12.6),1)
        my_fake_packet.CURRENT = round(random.uniform(0.0, 5.0),1)
        my_fake_packet.GYRO_R = round(random.uniform(-180, 180),1)
        my_fake_packet.GYRO_P = round(random.uniform(-180, 180),1)
        my_fake_packet.GYRO_Y = round(random.uniform(-180, 180),1)
        my_fake_packet.ACCEL_R = round(random.uniform(-10, 10),1)
        my_fake_packet.ACCEL_P = round(random.uniform(-10, 10),1)
        my_fake_packet.ACCEL_Y = round(random.uniform(-10, 10),1)
        my_fake_packet.GPS_ALTITUDE += 1
        my_fake_packet.GPS_LATITUDE = round(random.uniform(-90, 90),4)
        my_fake_packet.GPS_LONGITUDE = round(random.uniform(-180, 180),4)
        my_fake_packet.GPS_SATS = round(random.randint(0, 12),1)

def build_my_fake_packet():
     return (f"{my_fake_packet.TEAM_ID},{my_fake_packet.MISSION_TIME},{my_fake_packet.PACKET_COUNT},{my_fake_packet.MODE},{my_fake_packet.STATE},{my_fake_packet.ALTITUDE},{my_fake_packet.TEMPERATURE},{my_fake_packet.PRESSURE},{my_fake_packet.VOLTAGE},{my_fake_packet.CURRENT},{my_fake_packet.GYRO_R},{my_fake_packet.GYRO_P},{my_fake_packet.GYRO_Y},{my_fake_packet.ACCEL_R},{my_fake_packet.ACCEL_P},{my_fake_packet.ACCEL_Y},{my_fake_packet.GPS_TIME},{my_fake_packet.GPS_ALTITUDE},{my_fake_packet.GPS_LATITUDE},{my_fake_packet.GPS_LONGITUDE},{my_fake_packet.GPS_SATS},{my_fake_packet.CMD_ECHO}")


def send_telemetry():
    
    randomize()

    packet_string = build_my_fake_packet()

    print("Sending packet:", packet_string)

    My_device.send_data_async(receiver, packet_string)




def callback_function(xbee_message):
    try:
        #Receiving the raw data from radio and parsing it so that we can read it properly
        raw_bytes = xbee_message.data
        line = raw_bytes.decode('utf-8').strip()
        data = line.split(',')
        
        print("Received packet:", data)
        
        if len(data) < 2:
            print("Invalid command packet")
            return
    

        #Validation of command, ensuring it was our packet that we sent via ground station
        
        
        cmd  = data[2]

        if data[0] != "CMD":
            print("Invalid command prefix")
            return
        
        if data[1] != str(my_fake_packet.TEAM_ID):
            print("Packet not for this team")
            return



        if cmd == "SIM":
            
            if len(data) < 3:
                print("SIM command missing argument")
                return

            if data[3] == "ENABLE":
                my_fake_packet.CMD_ECHO = "SIM ENABLE"

            elif data[3] == "ACTIVATE":
                my_fake_packet.CMD_ECHO = "SIM ACTIVATE"

            elif data[3] == "DISABLE":
                my_fake_packet.CMD_ECHO = "SIM DISABLE"

        elif cmd == "CX":
            if data[3] == "ON":
                my_fake_packet.TX_ENABLED = True
                my_fake_packet.CMD_ECHO = "CXON"
                
            elif data[3] == "OFF":
                my_fake_packet.TX_ENABLED = False
                my_fake_packet.CMD_ECHO = "CXOFF"
        
        elif cmd == "ST":
            time_arg = data[3]

            if time_arg == "GPS":
                datetime.strptime(time_arg, "%H:%M:%S")
                my_fake_packet.MISSION_TIME = time_arg
                my_fake_packet.CMD_ECHO = "ST_GPS"

            else:
                
                try:
                    utc_now = datetime.now(timezone.utc)
                    my_fake_packet.MISSION_TIME = utc_now.strftime("%H:%M:%S")
                    my_fake_packet.CMD_ECHO = "ST"
                except ValueError:
                    print("Invalid time format for ST command")
        
        elif cmd == "SIMP":
            try:
                pressure_input = data[3]
                print(f"Received SIMP Value{pressure_input}")
                my_fake_packet.PRESSURE = pressure_input
                my_fake_packet.CMD_ECHO = "SIMP"
                
            except (ValueError, IndexError):
                print("Invalid Simulation Command Format")
        
        elif cmd == "CAL":
            my_fake_packet.ALTITUDE = 0
            my_fake_packet.GPS_ALTITUDE = 0
            print("Recieved CAL Input")
            my_fake_packet.CMD_ECHO = "CAL"

        
        
        else:
            print("Unknown command:", cmd)
            return

        print("Command processed:", my_fake_packet.CMD_ECHO)
    except Exception as e:
        print("ERROR receiving command:", e)





#Xbee Setup

My_device = XBeeDevice("COM6", 9600)
receiver = RemoteXBeeDevice(x64bit_addr=XBee64BitAddress.from_hex_string("0013A200423D8F47"), local_xbee=My_device)

try:
    My_device.open()
except:
    print("Could not open XBEE.")
    quit()

#Receiving Commands from the Ground Station

My_device.add_data_received_callback(callback_function)
    
while True:
    
    
    #Sending Fake Packet to the Radio
    if getattr(my_fake_packet, "TX_ENABLED", True):
        send_telemetry()
    else:
        print("Telemetry paused (CXOFF)")
    
    time.sleep(1)

    

   
My_device.close()

