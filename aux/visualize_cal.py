#!/usr/bin/env python3
#
#usage: ./aux/visualize_cal.py ~/.tareator/register.tareas-personal.csv

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json, sys, os
from datetime import datetime
import traceback

if __name__ == "__main__":

    try:

        for arg in sys.argv[1:]:

            tstamps = { int(datetime.fromisoformat(line.split(',')[0]).timestamp()): 1 for line in open(arg).readlines() }

            #tstamps = { int(datetime.fromisoformat(line.split(',')[0]).timestamp()): 1 if line.split(',')[1]=="Project A" else -1 for line in open(sys.argv[1]).readlines() }


            with open(f"cal-heatmap/data-{os.path.basename(arg)}.json", "w") as f:
                json.dump(tstamps, f, indent=2)

        os.chdir('cal-heatmap')

        LISTEN = ('localhost', 8000)
        httpd = HTTPServer(LISTEN, SimpleHTTPRequestHandler)
        print(f"Serving on http://{LISTEN[0]}:{LISTEN[1]}")
        httpd.serve_forever()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        #TODO: handle exceptions
        print(f"ERROR\n{traceback.format_exc()}",file=sys.stderr)
    finally:
        httpd.server_close()
