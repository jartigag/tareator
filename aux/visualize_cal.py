#!/usr/bin/env python3
#
#usage: ./aux/visualize_cal.py ~/.tareator/register.tareas-personal.csv

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json, sys
from datetime import datetime
import traceback

if __name__ == "__main__":

    try:

        tstamps = { int(datetime.fromisoformat(line.split(',')[0]).timestamp()): 1 for line in open(sys.argv[1]).readlines() }

        #tstamps = { int(datetime.fromisoformat(line.split(',')[0]).timestamp()): 1 if line.split(',')[1]=="Project A" else -1 for line in open(sys.argv[1]).readlines() }

        with open("cal-heatmap/data.json", "w") as f:
            json.dump(tstamps, f, indent=2)

        LISTEN = ('localhost', 8000)
        httpd = HTTPServer(LISTEN, SimpleHTTPRequestHandler)
        print(f"Serving on http://{LISTEN[0]}:{LISTEN[1]}/cal-heatmap/")
        httpd.serve_forever()

    except Exception as e:
        #TODO: handle exceptions
        print(f"ERROR\n{traceback.format_exc()}",file=sys.stderr)
