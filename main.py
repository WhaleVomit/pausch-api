import time
import json
import Queue

from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import lumiversepython as L


rig = L.Rig('/home/teacher/Lumiverse/PBridge.rig.json')
rig.init()
rig.run()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

q = Queue.Queue()


@app.route('/', methods=['GET', 'POST'])
def hello_world():
  if request.method == 'POST':
    content = request.get_json(force=True)

    red = float(content['red'])
    blue = float(content['blue'])
    green = float(content['green'])	
    
    for i in range(130):
      newred = red-float(i)*red/84
      rig.select('$sequence=' + str(i)).setRGBRaw(newred,green,blue)
      time.sleep(0.25)
      rig.select('$sequence=' + str(i)).setRGBRaw(0,0,0)
    
    return 'Successfully updated'
  
  else:	 # request.method == 'GET'
    rig.select('$all').setRGBRaw(0,0,0)
    return 'Hello, World!'


# Converts Hex Dictionary to Python List
def hex_to_rgb(cpanels):
  num_panels = len(cpanels)
  rgbs = []

  for i in range(num_panels):
    h = cpanels[str(i)][1:]
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
    rgbs.append(rgb)

  return rgbs


# displays the rgb colors on the respective panels on the bridge
def disp_rgb(rgbs):
	for i in range(len(rgbs)):
		rgb = rgbs[i]
		for j in range(5):
			set_panel(52+j-i*5,rgb)

# converts 0-255 color to 0-1
def color_to_raw(rgb):
    return [float(rgb[0])/255, float(rgb[1])/255, float(rgb[2])/255]

# set panel at idx to rgb value (0-255)
def set_panel(idx, rgb):
    rgbRaw = color_to_raw(rgb)
    rig.select("$panel=" + str(idx)).setRGBRaw(rgbRaw[0], rgbRaw[1], rgbRaw[2])

# set sequence at idx to rgb value (0-255)
def set_sequence(idx, rgb):
    rgbRaw = color_to_raw(rgb)
    rig.select('$sequence=' + str(idx)).setRGBRaw(rgbRaw[0], rgbRaw[1], rgbRaw[2])

@app.route('/theme', methods=['GET','POST'])
@cross_origin()
def foo():
  if request.method == 'POST':
    content = request.get_json()
    q.put(content)
    return str(q.qsize())

  # request.method == 'GET'
  if q.qsize()==0:
    return "empty q"

  qtop = q.get()
  cname = qtop["name"]
  cpanels = qtop["panels"]
  rgbs = hex_to_rgb(cpanels)
  disp_rgb(rgbs)

  return str(rgbs[0])

# processes json files with "events"
@app.route('/themes', methods=['GET'])
def themesmethod():
  if request.method == 'GET':
    if q.qsize()==0:
      return "empty q"
  
  qtop = q.get()
  cname = qtop["name"]
  cevents = qtop["events"]

  numevents = len(cevents)
  rgbs = []
  
  for i in range(numevents):
    cevent = cevents[str(i)]
    cpanels = cevent["panels"]
    rgbs = hex_to_rgb(cpanels)

    cdur = cevent["duration"]
    disp_rgb(rgbs)
    time.sleep(int(cdur))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True)
