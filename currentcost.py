#!/usr/bin/env python

# XML lib
from currentcostlib import Packet
import serial
import sys
import argparse

parser = argparse.ArgumentParser(description='Read XML packages from Current Cost monitor and log power and temperature readings.')
parser.add_argument('--device', metavar='DEV', default='/dev/ttyUSB0', 
                    help='the serial device to read from')
parser.add_argument('--raw', action='store_true',
                    help='log raw data into a file raw.log')
parser.add_argument('--log', action='store_true',
                    help='write single line data points into a text file parsed.log')
parser.add_argument('-o', '--stdout', action='store_true',
                    help='print messages to stdout')
parser.add_argument('--influx', action='store_true',
                    help='write single line data points into file influx.log suitable for InfluxDB import')
parser.add_argument('--logdir', type=argparse.FileType('dir'), 
                    help='directory to store log files into')
parser.add_argument('--mqttserver', metavar='HOST', default='localhost',
                    help='MQTT host to connect to')
parser.add_argument('--mqttport', metavar='P', type=int,  default='1883',
                    help='MQTT port to connect to')
parser.add_argument('--mqtttopic', metavar='TOPIC',
                    help='MQTT topic root, e.g., foobar/currentcost/.  If set attempt to log data to MQTT broker. Will publish to TOPIC/temp, TOPIC/ccmontime and TOPIC/watts.')
parser.add_argument('--mqttuser', default='', help='MQTT user name')
parser.add_argument('--mqttpassword', default='', help='MQTT password')
parser.add_argument('--mqttcacerts', default='', help='String path to trusted CA certificates for MQTT TLS server authentication.')

args = parser.parse_args()

conn = serial.Serial(args.device,baudrate=57600, timeout=30)

if args.mqttuser:
    mqtt_auth = {'username':args.mqttuser, 'password':args.mqttpassword}
else:
    mqtt_auth = None

if args.mqttcacerts:
    mqtt_tls = {'ca_certs':args.mqttcacerts}
else:
    mqtt_tls = None


# canonicalize log directory arg
if args.logdir:
    args.log_dir = args.log_dir.rstrip('/') + '/'

# Every six seconds, we get a chunk of XML terminated by a newline
while 1:
    try:
        p = Packet(conn)
        if args.log:
            p.log(args.logdir)
        if args.stdout:
            p.log_stdout()
        if args.raw:
            p.log_raw(args.logdir)
        if args.influx:
            p.log_influx(args.logdir)
        if args.mqtttopic:
            p.mqtt_publish(args.mqtttopic,args.mqttserver,args.mqttport,mqtt_auth,mqtt_tls)
    except (IOError, KeyboardInterrupt, SystemExit):
        raise
    except:
        print("Error in parsing packet, ignoring.")
