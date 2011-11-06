import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
import random
from datetime import datetime

# CONFIGURE THESE VARIABLES FOR YOUR OWN APPLICATION
NUM_NODES = 2
FILE_DIRECTORY = os.path.join(os.path.dirname(__file__), "static/example_data_vsmall")
FILE_LIST = os.listdir(FILE_DIRECTORY)

# WRITE THE SERVER REDUCE FUNCTION FOR YOUR OWN APPLICATION
# this function should eventually go into javascript once we've added support
# for client reducers via NativeClient.  For now we're stuck doing reduce() on the server.
def reduce():
    words = dict()
    for line in map_results.strip().split("\n"):
        word = line.split(" ")[0]
        count = int(line.split(" ")[1])
        if words.get(word) == None:
            words[word] = 0
        words[word] += count
    results = ''.join([k + " " + str(v) + "\n" for k,v in words.iteritems()])
    return results


listeners = []
num_completed_nodes = 0 # number of nodes that have done their map jobs and responded
map_results = "" # add to the results here as mappers return stuff
map_start = ""
map_end = ""
reduce_start = ""
reduce_end = ""

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        items = []
        self.render('worker.html', items=items)

class ParaSiteWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        if len(listeners) < NUM_NODES:
            print "WebSocket opened by " + self.request.remote_ip + "."
            listeners.append(self)
            if len(listeners) == NUM_NODES:
                self.allocate_files()
                self.do_map()
        else:
            # TODO properly handle what should happen to late-comers
            print "WebSocket open request rejected for client " + \
            self.request.remote_ip + ": already accepted sufficient clients." 
        

    def on_message(self, message):
        global map_results
        global num_completed_nodes
        themessage = json.loads(message)
        if themessage['command'] == 'results':
            print "CLIENT: " + self.request.remote_ip + " sent results."
            map_results += themessage['contents']
            num_completed_nodes += 1
            if num_completed_nodes == NUM_NODES:
                global map_end
                map_end = datetime.now()
                print "client maps took " + str(map_end-map_start)
                global reduce_start
                reduce_start = datetime.now()
                final_results = reduce()
                global reduce_end
                reduce_end = datetime.now()
                print "server reduce took " + str(reduce_end-reduce_start)
                num_completed_nodes = 0 #reset in case of further jobs
                print "Final results are:\n" + final_results
        elif themessage['command'] == 'opened':
            print "CLIENT " + self.request.remote_ip + " opened websocket."

    def on_close(self):
        print "WebSocket to " + self.request.remote_ip + " closed."
        listeners.remove(self)

    def allocate_files(self):
        for f in FILE_LIST:
            fpath = os.path.join(FILE_DIRECTORY, f)
            msg = dict()
            msg['command'] = 'file'
            msg['identifier'] = f.split('.')[0] # files are identified by their name minus extension
            with open(fpath) as thefile:
                msg['contents'] = thefile.read() 
            recipient = random.choice(listeners)
            recipient.write_message(json.dumps(msg))
            print 'SERVER: allocated ' + f + ' with identifier ' + msg['identifier']
            
    def do_map(self):
        global map_start
        map_start = datetime.now()
        for listener in listeners:
            msg = dict()
            msg['command'] = 'map'
            listener.write_message(json.dumps(msg))


        

settings = {"static_path": os.path.join(os.path.dirname(__file__), "static"),}

application = tornado.web.Application([
        (r"/", MainHandler),(r"/websocket", ParaSiteWebSocket),
        ], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
