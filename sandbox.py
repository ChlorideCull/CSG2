import copy
import csgwsgiclasses

class csg2api:
    def __init__(self, bottleapp, sessionlist, threadlocal):
        self.app = bottleapp
        self.authhook = None
        self.sessions = sessionlist
        self.localdata = threadlocal
    def route(self, routestr, method='GET'):
        return lambda callable: self.app.add_route(routestr, callable, method)
    def get_request(self):
        if "_httprequestobj" not in self.localdata:
            self.localdata["_httprequestobj"] = csgwsgiclasses.HTTPRequest(self.localdata)
        return self.localdata["_httprequestobj"]
    def get_response(self):
        if "_httpresponseobj" not in self.localdata:
            self.localdata["_httpresponseobj"] = csgwsgiclasses.HTTPResponse(self.localdata)
        return self.localdata["_httpresponseobj"]
    def get_username_of_request(self):
        return self.sessions[csgwsgiclasses.HTTPRequest(self.localdata).get_cookies()["csg2sess"].value]
    def auth(self, func):
        self.authhook = func

freshglobals = {
    "__name__": "CSG2 Site Script",
    "__builtins__": globals()["__builtins__"],
    "__loader__": globals()["__loader__"]
}

def create_box(sauce, bottleapp, apiclass, addglobals={}):
    newglobals = copy.copy(freshglobals)
    newglobals["csg2api"] = apiclass
    newglobals.update(addglobals)
    exec(sauce, newglobals)
