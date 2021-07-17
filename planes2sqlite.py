#! /usr/bin/env python3

import sqlite3
import json
from datetime import datetime
import time
import signal
import sys
import os 


LOCKFILE='planes2sqlite.lock'
CURFILE='current.db'
DEST='10.1.0.1:/data/flight-tracker'


now = datetime.now()
lockfile = os.open(LOCKFILE, os.O_CREAT|os.O_EXCL|os.O_WRONLY,mode=0o644)

if lockfile < 0: 
    sys.stderr.write("Could not open %s or already exists, is process running or improperly killed? bailing\n" % (LOCKFILE)); 
    sys.exit(1) 

os.close(lockfile) 



if os.path.exists(CURFILE):  
    name="%04d.%02d.%02d-%02d%02d%02d.db" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    print("Moving %s to %s and gzipping" %(CURFILE, name))
    os.system("mv %s %s && gzip %s" %(CURFILE,name,name))
    print("Copying %s.gz to %s" %(name, DEST))
    os.system("rsync -avh %s.gz %s" %(name,DEST))

#check if there is already an current.db

conn = sqlite3.connect(CURFILE);

stop = False

def signal_handler(a,b):
    sys.stdout.write("Stopping!\n")
    conn.commit()
    conn.close()
    os.remove(LOCKFILE) 
    sys.exit(0)


cur = conn.cursor()

cur.execute("CREATE TABLE aircraft (id int primary key, latitude real, longitude real, altitude real, seen real, rssi real, flightnumber varchar, hexcode varchar, track real, speed real, vertrate real, readtime datetime default current_timestamp);")


current_time= 0
print("Press Ctrl-C to stop\n")
signal.signal(signal.SIGINT,signal_handler)
signal.signal(signal.SIGTERM,signal_handler)

howmany=0

last_printout = now.timestamp() 

while True:
    f = open("/run/dump1090-mutability/aircraft.json");
    j = json.loads(f.read())

    this_time = float(j["now"])

    if this_time <= current_time:
        continue

    current_time = this_time

    now = datetime.fromtimestamp(this_time)

    for aircraft in j['aircraft']:


        hexcode = aircraft['hex'] if 'hex' in aircraft else "N/A"
        flight = aircraft['flight'] if 'flight' in aircraft else "N/A"

        lat = float(aircraft['lat']) if 'lat' in aircraft else -9999
        lon = float(aircraft['lon']) if 'lon' in aircraft else -9999
        alt = ( -1 if aircraft['altitude'] == 'ground' else float(aircraft['altitude']))  if 'altitude' in aircraft else -9999
        track = float(aircraft['track']) if 'track' in aircraft else -9999
        speed = float(aircraft['speed']) if 'speed' in aircraft else -9999
        vertrate = float(aircraft['vert_rate']) if 'vert_rate' in aircraft else -9999
        rssi = float(aircraft['rssi'])
        seen = float(aircraft['seen'])

        cur.execute("INSERT INTO aircraft(latitude, longitude, altitude, flightnumber, hexcode, readtime,rssi,seen,vertrate,speed,track) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (lat,lon,alt,flight,hexcode,now,rssi,seen,vertrate,speed,track))
        howmany+=1

    if (datetime.now().timestamp() - last_printout > 30): 
        print("Recorded %d positions at in last 30 seconds" % (howmany))
        howmany=0
        last_printout=datetime.now().timestamp() 
    conn.commit() 
    time.sleep(3);
