from uuid import uuid4
import argparse
from threading import Event, Thread
from time import sleep
# import sys
# sys.path.insert(0,'/users/ugrad/brennar5/ruth/cs7ns1-meshd/')
# sys.path.insert(0,'/Users/ruthbrennan/Documents/5th_Year/cs7ns1-meshd/')

from sensor import Sensor

SENSOR_INTERVAL = 5


def run_sensor(sensor: Sensor, sensorType, stop: Event):
    while not stop.is_set():
        data = sensor.generate_data(sensorType)
        sensor.send_data(data)
        sleep(SENSOR_INTERVAL)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sensortype', help='Sensor Type Specification', required=True)
    parser.add_argument('--sensorport', help='Sensor Port Specification', required=True)
    args = parser.parse_args()

    if args.sensortype is None:
        print("Please specify the type of sensor")
        exit(1)

    if args.sensorport is None:
        print("Please specify the sensor port")
        exit(1)

    sensor_type = args.sensortype
    sensor_port = args.sensorport

    try:
        session = uuid4()
        print('Sensor Session %s started' % (session))

        sensor = Sensor(sensor_type, session, sensor_port)
        stop = Event()

        sensor_thread = Thread(target=run_sensor, args=(sensor, sensor_type, stop))
        sensor_thread.start()
        sensor_thread.join()

    finally:
        stop.set()