import lumiversepython as L
import time

rig = L.Rig("/home/teacher/Lumiverse/PBridge.rig.json")
rig.init()
rig.run()

while(1):
    for j in range(3):
        a = j
        b = (j + 1) % 3
        c = (j + 2) % 3
        for i in range(4,19):
            rig.select("$panel="+str(i*3+a)).setRGBRaw(46./255,160./255,177./255)
            rig.select("$panel="+str(i*3+b)).setRGBRaw(33,41,55)
            rig.select("$panel="+str(i*3+c)).setRGBRaw(230,231,232)

        time.sleep(1)

