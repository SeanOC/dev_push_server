import time
from datetime import datetime

from dateutil.parser import parse as parse_timestr
from dateutil.tz import tzutc

from werkzeug import Request, Response, ClosingIterator, Local, LocalManager
from werkzeug.routing import Map, Rule

local = Local()
local_manager = LocalManager([local])
application = local('application')

class PushServer(object):
    def __init__(self):
        local.application = self
        
        self.url_map = Map([
            Rule('/activity/', endpoint="subscribe"),
            Rule('/publish/', endpoint="update"),
        ])
        self.views = {
            'subscribe': self.on_subscribe,
            'update': self.on_update,
        }
        self.updates = []
        self.max_updates = 5


    def on_subscribe(self, request):
        last_modified = local.last_modified = request.headers.get('last_modified', None)
        if last_modified is not None:
            last_modified = parse_timestr(last_modified)
        
        local.next_update = next_update = self.get_next_update(last_modified)
        while (next_update is None):
            time.sleep(1)
            next_update = self.get_next_update(last_modified)
        
        return self.send_update(next_update)
        
    def send_update(self, update):
        response = Response(
            response=update['body'],
            content_type=update['content_type'],
        )
        response.last_modified = update['published_on']
        
        return response
        
                
    def get_next_update(self, last_modified):
        next_update = None
        for update in self.updates:
            if last_modified is None or update['published_on'] > last_modified:
                next_update = update
                break;
                
        return next_update
    
    def on_update(self, request):
        if request.method == 'POST' or request.method == 'PUT':
            update = {
                'body': request.data,
                'content_type': request.content_type,
                'published_on': datetime.now(tzutc()),
            }
        
            if len(self.updates) >= self.max_updates:
                self.updates = self.updates[-(self.max_updates - 1):]
        
            self.updates.append(update)
            response = Response(response="Update Accepted", status=201)
        else:
            response = Response(response="Method not allowed", status=405)
            
        return response
    
    def __call__(self, environ, start_response):
        local.application = self
        request = Request(environ)
        local.url_adapter = urls = self.url_map.bind_to_environ(environ)
        response = urls.dispatch(lambda e, v: self.views[e](request, **v),
                                catch_http_exceptions=True)
                                
        return response(environ, start_response)#, [local_manager.cleanup,])