import copy

class csg2api:
    def __init__(self, bottleapp):
        self.app = bottleapp
        self.agpl = False # If True, allow deeper integration
    def route(self, *args, **kwargs):
        return self.app.route(*args, **kwargs)
    def auth(self, func):
        self.authhook = func

freshglobals = {
    "__name__": "CSG2 Site Script",
    "__builtins__": globals()["__builtins__"],
    "__loader__": globals()["__loader__"]
}

def create_box(sauce, bottleapp, addglobals={}):
    newglobals = copy.copy(freshglobals)
    newglobals["csg2api"] = csg2api(bottleapp)
    newglobals.update(addglobals)
    exec(sauce, newglobals)
