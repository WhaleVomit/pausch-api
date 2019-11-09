from flask import Flask
from flask import request
import lumiversepython as L
import time
import json

import Queue
from flask_cors import CORS, cross_origin

rig = L.Rig('/home/teacher/Lumiverse/PBridge.rig.json')
rig.init()
rig.run()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        content = request.get_json(force=True)
        print content
	red = float(content['red'])
	blue = content['blue']
	green = content['green']
	for i in range(130):
	    newred = red-float(i)*red/84
	    print newred
	    rig.select('$sequence=' + str(i)).setRGBRaw(newred,green,blue)
            time.sleep(0.25)
	    rig.select('$sequence=' + str(i)).setRGBRaw(0,0,0)
        return 'Successfully updated'
    else:
        rig.select('$all').setRGBRaw(0,0,0)
        return 'Hello, World!'

@app.route('/hello')
def something():
	q2 = Queue.Queue()
	q2.put("1")
	q2.put("2")
	return q2.get()

q = Queue.Queue()

@app.route('/sleep')
def sleeping():
    time.sleep(10)
    return "Done sleeping"

# converts hex dict to rgb list
def hex_to_rgb(cpanels):
	numpanels = len(cpanels)
	rgbs = []
	for i in range(numpanels):
		h = cpanels[str(i)]
		h = h[1:]
		rgb = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
		rgbs.append(rgb)
	return rgbs

# displays the rgb colors on the respective panels on the bridge
def disp_rgb(rgbs):
	for i in range(len(rgbs)):
		rgb = rgbs[i]
		for j in range(5):
			rig.select("$panel="+str(52+j-i*5)).setRGBRaw(float(rgb[0])/255,float(rgb[1])/255,float(rgb[2])/255)


@app.route('/theme', methods=['GET','POST'])
@cross_origin()
def foo():
    if request.method == 'POST':
        # print request.headers
	# print request.headers.get('Content-Type')
	content = request.get_json()
        q.put(content)
	# parsed = json.loads(content)
	# print content
	# print json.dumps(parsed, indent=4, sort_keys=True)

	# response = Flask.jsonify({'size': str(q.qsize())})
	# response.headers.add('Access-Control-Allow-Origin','*')
	# return response
	return str(q.qsize())
    if request.method == 'GET':
	if q.qsize()==0:
		return "empty q"
	qtop = q.get()
	cname = qtop["name"]
	# cid = qtop["id"]
	print cname
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
	cid = qtop["id"]
	print cid
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

