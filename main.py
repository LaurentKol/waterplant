#!/usr/bin/python
import time, datetime, dateutil.relativedelta, signal, sys, socket, logging, xmlrpclib, threading
from SimpleXMLRPCServer import SimpleXMLRPCServer
import subprocess,re
import RPi.GPIO as GPIO
from Adafruit_ADS1x15 import ADS1x15
import Adafruit_DHT
import json

# Flask is used for REST api
from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin

logging.basicConfig(filename='/var/log/water-plant.log',format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S', filemode='w', level=logging.DEBUG)

GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)

watering = False # this can be changed via XMLRPC
moisture_threshold = 400
watering_schedule = ['09:00','09:30']
LAST_WATERING_THRESHOLD = 300
WATERING_DURATION = 30

PIN_DHT_SENSOR = 7
PIN_MOISTURE_SWITCH = [23,21,24,22]
PIN_MOISTURE_SENSOR = [0,1,3,2]
PIN_PUMP_RELAY = [8,10,16,18]

CARBON_SERVER = '192.168.x.x'
CARBON_PORT = 2003
GRAPHITE_PREFIX = 'environmental.xxxxx.balcony'

# Enable REST API
LISTENING_IP='0.0.0.0'
app = Flask(__name__)
app.use_reloader=False
app.debug = False
CORS(app)

@app.route("/get/mode")
def rest_api_get_mode():
  try:
    moisture_level
  except NameError:
    moisture_level_tmp = ['N/A','N/A','N/A','N/A']
  else:
    moisture_level_tmp = moisture_level

  def time_diff_human_readable(t):
    dt1 = datetime.datetime.fromtimestamp(int(t))
    dt2 = datetime.datetime.fromtimestamp(int(time.time()))
    rd = dateutil.relativedelta.relativedelta (dt2, dt1)
    if rd.months > 0:
      return "%dmths" % rd.months
    elif rd.days > 0:
      return "%dd" % rd.days
    elif rd.hours > 0:
      return "%dh" % rd.hours
    elif rd.minutes > 0:
      return "%dmin" % rd.minutes
    else:
      return "%dsec" % rd.seconds

  last_watering_formatted = map((lambda x: time_diff_human_readable(x)),last_watering)
  return json.dumps({'watering_mode' : watering, 'moisture_threshold' : moisture_threshold, 'moisture_level' : moisture_level_tmp, 'watering_schedule' : watering_schedule, 'last_watering' : last_watering_formatted})

# TODO: add reqparse.RequestParser to validate choices, e.g: on/off
@app.route("/set/mode/<string:status>")
def rest_api_set_watering_mode(status):
  watering = status
  logging.info("watering mode changed to: %s" % status)
  return 'watering_mode set to: %s' % status

server_thread = threading.Thread(target=app.run,kwargs={'host':LISTENING_IP})
server_thread.setDaemon(True)
server_thread.start()

# Enable network commands via XMLRPC
XMLRPC_LISTEN_IP = '0.0.0.0'
XMLRPC_PORT = 55000
def set_watering_mode(mode):
  if not isinstance(mode,bool):
    return 'set_watering_mode func only accepts bool!'
  global watering ; watering = mode
  logging.info("watering mode changed to: %s" % mode)
  return 'watering_mode set to: %s' % mode

def set_moisture_threshold(v):
  v = int(v)
  #if not isinstance(v,int) or not (0 < v < 2000):
  if not (0 < v < 2000):
    logging.warn("Invalid value received for moisture_threshold: %s" % v)
    return 'set_moisture_threshold func only accepts int!'
  global moisture_threshold ; moisture_threshold = v
  logging.info("moisture_threshold changed to: %s" % v)
  return 'moisture_threshold set to: %s' % v

def set_watering_schedule(from_hours,to_hours):
  re_hours = re.compile('^[0-9][0-9]:[0-9]{2}$')
  if re_hours.match(from_hours) and re_hours.match(to_hours):
    global watering_schedule ; watering_schedule = [from_hours,to_hours]
    logging.info("watering_schedule changed to: %s .. %s" % (from_hours,to_hours))
    return "watering_schedule changed to: %s .. %s" % (from_hours,to_hours)
  else:
    logging.warn("Invalid value received for watering_schedule: %s - %s" % (from_hours,to_hours))
    return 'watering_schedule func only 2 strings, e.g: "09:00" "09:30"'

def get_mode():
  try:
    moisture_level
  except NameError:
    moisture_level_tmp = ['N/A','N/A','N/A','N/A']
  else:
    moisture_level_tmp = moisture_level

  return {'watering_mode' : str(watering), 'moisture_threshold' : moisture_threshold, 'moisture_level' : moisture_level_tmp, 'watering_schedule' : watering_schedule }

server = SimpleXMLRPCServer((XMLRPC_LISTEN_IP, XMLRPC_PORT))
server.register_function(set_watering_mode, "set_watering_mode")
server.register_function(set_moisture_threshold, "set_moisture_threshold")
server.register_function(set_watering_schedule, "set_watering_schedule")
server.register_function(get_mode, "get_mode")
server_thread = threading.Thread(target=server.serve_forever)
server_thread.setDaemon(True)
server_thread.start()

def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
#print 'Press Ctrl+C to exit'

def send_graphite(measurements):
  message = ''
  now = int(time.time())
  for key, value in measurements.iteritems():
    message += '%s.%s %s %i\n' % (GRAPHITE_PREFIX,key,value,now)
  #logging.debug(message)

  sock = socket.socket()
  try:
    sock.connect((CARBON_SERVER, CARBON_PORT))
    sock.sendall(message)
    #logging.debug('Moisture level sent to Graphite successfully')
  except socket.error as msg:
    logging.error("Failed to send to Graphite: %s" % msg)
  sock.close()

def read_rpi_cpu_temp():
  raw_output = subprocess.check_output(['/opt/vc/bin/vcgencmd', 'measure_temp']).strip()
  temp_str = re.sub(r'.*temp=([0-9.]+).*', r'\1', raw_output)
  logging.debug('Rpi CPU : temperature = %.1f' % float(temp_str))
  return float(temp_str)


def read_dht_sensor():
  humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, PIN_DHT_SENSOR)
  if humidity and temperature:
    logging.debug('DHT sensor : humidity = %.1f , temperature = %.1f' % (humidity, temperature))
    return ('%.1f' % float(humidity),'%.1f' % float(temperature))
  else:
    logging.warn('Could not read from DHT sensor')
    return False,False

def read_moisture_sensor():
  moisture = []
  for pin in PIN_MOISTURE_SWITCH:
    GPIO.output(pin, True)
  
  time.sleep(1)
  
  for i, pin in enumerate(PIN_MOISTURE_SENSOR):
    volts = adc.readADCSingleEnded(pin, gain, sps) #/ 1000
    moisture.append(int(volts))
  logging.debug('Moisture sensors ' + str(moisture))
  
  for pin in PIN_MOISTURE_SWITCH:
    GPIO.output(pin, False)
  
  return moisture

def water_plant(i):
  pin = PIN_PUMP_RELAY[i]
  logging.info("Turning on pump %i for %i sec (%s), %i < %i" % (i,WATERING_DURATION,watering,moisture_level[i],moisture_threshold))
  if watering:
    last_watering[i] = now
    GPIO.output(pin, False)
    time.sleep(WATERING_DURATION)
    GPIO.output(pin, True)

def is_watering_time():
  try:
    global watering_schedule
    start,end =  watering_schedule
    start_dt = datetime.time(*map(int,start.split(':')))
    end_dt   = datetime.time(*map(int,end.split(':')))
    now_dt   = datetime.datetime.now().time()

    if start_dt <= end_dt:
      return start_dt <= now_dt <= end_dt
    else:
      return start_dt <= now_dt or now_dt <= end_dt
  except Exception as e:
    logging.warn('Could not check watering_schedule: %s' % e.message )
    return False
  

# Initialize
ADS1015 = 0x00  # 12-bit ADC
gain = 2870
sps = 128  # 128 samples per second

#Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, PIN_DHT_SENSOR) # 1st measurement unaccurate

adc = ADS1x15(ic=ADS1015)

for pin in PIN_MOISTURE_SWITCH + PIN_PUMP_RELAY:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, True) # Set all off

# Main
now = int(time.time())
last_watering = [now,now,now,now]

logging.info('Watering mode: %s' % watering)
logging.info('Moisture threshold: %i' % moisture_threshold)
logging.info('Last watering threshold: %i' % LAST_WATERING_THRESHOLD)
logging.info('Watering duration: %i' % WATERING_DURATION)

while True:
  moisture_level = read_moisture_sensor()
  humidity, temperature = read_dht_sensor()
  rpi_temperature = read_rpi_cpu_temp()
  graphite_d = {}

  if humidity and temperature:
    graphite_d.update({'temperature': temperature, 'humidity': humidity})

  if rpi_temperature:
    graphite_d.update({'rpi_temperature': rpi_temperature})

  for i, v in enumerate(moisture_level):
    graphite_d['soil-moisture.%s' % i] = v
  send_graphite(graphite_d)

  #if time.localtime().tm_hour in range(0,24):
  if is_watering_time():
    for i, v in enumerate(moisture_level):
      now = int(time.time())
      if moisture_threshold > v:
        if LAST_WATERING_THRESHOLD < (now - last_watering[i]):
          water_plant(i)
        else:
          logging.debug("Sensor %i: %i < %i but recently watered, skipping for %i sec more" % (i,moisture_level[i],moisture_threshold,(last_watering[i] - now + LAST_WATERING_THRESHOLD )))
  else:
    logging.debug('Now is not in watering_schedule')

  time.sleep(10)

