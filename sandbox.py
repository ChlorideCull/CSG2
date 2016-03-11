import copy
from bottle import request

class csg2api:
    def __init__(self, bottleapp, sessionlist):
        self.app = bottleapp
        self.authhook = None
        self.agpl = False # If True, allow deeper integration
        self.sessions = sessionlist
    def route(self, *args, **kwargs):
        return self.app.route(*args, **kwargs)
    def get_username_of_request(self):
        return self.sessions[request.get_cookie("csg2sess")]
    def auth(self, func):
        self.authhook = func

freshglobals = {
    "__name__": "CSG2 Site Script",
    "__builtins__": globals()["__builtins__"],
    "__loader__": globals()["__loader__"]
}

def create_box(sauce, bottleapp, apiclass=None, addglobals={}):
    if apiclass == None:
        apiclass = csg2api(bottleapp)
    newglobals = copy.copy(freshglobals)
    newglobals["csg2api"] = apiclass
    newglobals.update(addglobals)
    exec(sauce, newglobals)
