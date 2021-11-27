from uuid import UUID, uuid4
import argparse
from threading import Event, Thread
from sensor import Sensor
from time import sleep

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

        discovery_recv_thread = Thread(target=run_sensor, args=(sensor, sensor_type, stop))
        discovery_recv_thread.start()
        discovery_recv_thread.join()

    finally:
        stop.set()