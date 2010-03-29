#!/usr/bin/env python

from werkzeug import script

def make_app():
    from application import PushServer
    return PushServer()

action_runserver = script.make_runserver(make_app, threaded=True, use_reloader=True)

script.run()