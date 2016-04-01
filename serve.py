#
#    ChlorideSiteGenerator 2
#    Copyright (C) 2016 Sebastian "Chloride Cull" Johansson
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import butcheredbottle
from waitress import serve as waitress_serve
import inspect
import os
import sass
import json
import argparse
import importlib
import sys
import glob
import random
import uuid
import re
import sandbox
import configman
import threading
import logging

class CSG2Server:
    runningsessions = {}
    route_res = []  # (regex object, callable)
    
    def __init__(self, themedir, siteconftemplate):
        self.threadlocal = threading.local()
        self.buboobj = butcheredbottle.Router()
        self.installdir = sys.path[0] # Note: this should ideally be gotten from somewhere else.
        self.apiclass = sandbox.csg2api(self, self.runningsessions)
        
        # Parse arguments
        argparser = argparse.ArgumentParser()
        argparser.add_argument('sitesfolder', metavar='<site storage folder>', help="path to the folder containing sites")
        argparser.add_argument('siteroot', metavar='<site name>', help="site name/the folder with config.json")
        self.parsedargs = argparser.parse_args()

        # Setup configuration and path to site
        self.sitepath = os.path.abspath(os.path.join(self.parsedargs.sitesfolder, self.parsedargs.siteroot))
        siteconffile = open(os.path.join(self.sitepath, "config.json"), mode="rt", encoding="utf-8")
        self.siteconf = configman.normalize_config(json.load(siteconffile), self.parsedargs.siteroot)
        siteconffile.close()
        
        # Setup theming
        themesroot = os.path.abspath(themedir)
        self.themepath = os.path.join(themesroot, self.siteconf["site"]["theme"])
        os.chdir(self.sitepath)
        
        # Assign routes
        self.add_route("/rand/<filepath:path>", self.getrandstaticredirect)
        self.add_route("/static/<filepath:path>", self.getstatic)
        self.add_route("/theme/sass/master.scss", self.compilethemesass)
        self.add_route("/theme/static/<filepath:path>", self.getthemeasset)
        self.add_route("/sass/<filename:re:.*\.scss>", self.compilesass)
        self.add_route("/", self.catchall)
        self.add_route("/<navpath:path>", self.catchall)

        self.dologin = self.wsgiapp.route("/auth/login", method="POST")(self.dologin)
        self.dologout = self.wsgiapp.route("/auth/logout")(self.dologout)
        
        # If they have code, run it
        if "additional_code" in self.siteconf["site"]:
            oldpath = sys.path
            sys.path[0] = self.sitepath
            importlib.invalidate_caches()
            with open(os.path.join(self.sitepath, self.siteconf["site"]["additional_code"]), mode="rt") as codefile:
                sandbox.create_box(codefile.read(), self, apiclass=self.apiclass) # This file is exempt from the linking clauses in the license, allowing it to be non-(A)GPL.
            sys.path = oldpath
            importlib.invalidate_caches()

        # Configure Nginx
        socketpath = "/tmp/csg2_{}.sock".format(self.siteconf["site"]["domain_name"].replace(".", "_"))
        print("-> Generating config.")
        with open(os.path.abspath(siteconftemplate), mode="rt", encoding="utf-8") as sitetemplate:
            sitetemplatetxt = sitetemplate.read()
            newsite = sitetemplatetxt.replace("%%SERVERNAME%%", self.siteconf["site"]["domain_name"]).replace("%%SOCKETPATH%%", socketpath)
            with open("/tmp/{}.csg2nginx".format(self.siteconf["site"]["domain_name"].replace(".", "_")), mode="wt", encoding="utf-8") as newconf:
                newconf.write(newsite)
        
        # Serve site.
        print("-> Serving up site on '{}'.".format(socketpath))
        waitress_serve(self, unix_socket=socketpath)

    def add_route(self, routestr, callable, method='GET'):
        matchobj = self.buboobj.get_regex(routestr)
        cachedobj = (matchobj[0], matchobj[1], re.compile(matchobj[2]))
        self.route_res.append((method, cachedobj, callable))
        return callable
    
    # Route: "/rand/<filepath:path>"
    def getrandstaticredirect(self, filepath):
        response = self.apiclass.get_response()
        extmap = {
            "image": ["png", "jpg", "jpeg", "gif"] # Using "image" as extention allows matching with all image types
        }
        response.status = (307, "Temporary Redirect")
        modfilepath = filepath.split(".")
        targetmap = modfilepath[-1:]
        matches = []
        if modfilepath[-1] in extmap.keys():
            targetmap = extmap[modfilepath[-1]]
        for ext in targetmap:
            modfilepathstr = ".".join(modfilepath[:-1] + ["*"] + [ext])
            matches = matches + glob.glob(os.path.join(self.sitepath, "static/", modfilepathstr))
        if len(matches) == 0:
            response.status = (404, "Not Found")
            return "Files not found."
        pick = random.choice(matches).replace(self.sitepath, "").replace("\\", "/")
        response.set_header("Location", pick)
        return ""

    # Route: "/static/<filepath:path>"
    def getstatic(self, filepath):
        response = self.apiclass.get_response()
        response.set_header("Cache-Control", "max-age=300")
        return static_file(filepath, root=os.path.join(self.sitepath, "static/"))

    # Route: "/theme/sass/master.scss"
    def compilethemesass(self):
        response = self.apiclass.get_response()
        output = ""
        response.set_header("Cache-Control", "max-age=300")
        response.set_header("Content-Type", "text/css")
        with open(os.path.join(self.sitepath, "scss/theme.scss"), mode="rt") as fl:
            output += fl.read()
        with open(os.path.join(self.themepath, "master.scss"), mode="rt") as fl:
            output += fl.read()
        return sass.compile(string=output)
    
    # Route: "/theme/static/<filepath:path>"
    def getthemeasset(self, filepath):
        response = self.apiclass.get_response()
        response.set_header("Cache-Control", "max-age=300")
        return static_file(filepath, root=os.path.join(self.themepath, "assets/"))

    # Route: "/sass/<filename:re:.*\.scss>"
    def compilesass(self, filename):
        output = ""
        response = self.apiclass.get_response()
        response.set_header("Cache-Control", "max-age=300")
        response.set_header("Content-Type", "text/css")
        if not os.path.exists(os.path.join(self.sitepath, "scss/" + filename)):
            response.status = (404, "Not Found")
            return "SCSS file not found."
        with open(os.path.join(self.sitepath, "scss/" + filename), mode="rt") as fl:
            output += fl.read()
        return sass.compile(string=output)

    def _match_page(self, requestpath, pagenavpath):
        if "%%" in pagenavpath:
            pagenavpathregex = re.escape(pagenavpath).replace("\\%\\%", "([^/]+)")
            matchobj = re.match(pagenavpathregex, requestpath)
            if matchobj == None:
                return False
            else:
                return matchobj.groups()
        else:
            return (requestpath == pagenavpath)
        
    # Route: "/"
    # Route: "/<navpath:path>"
    def catchall(self, navpath="index"):
        response = self.apiclass.get_response()
        pageindex = -1
        tplargs = ()
        for i in range(0, len(self.siteconf["pages"])):
            testmatch = self._match_page(navpath, self.siteconf["pages"][i]["navpath"])
            if type(testmatch) is tuple:
                tplargs = testmatch
                testmatch = True
            if testmatch:
                pageindex = i
                break
        templatepath = os.path.join(self.sitepath, self.siteconf["pages"][pageindex]["path"])
        if not os.path.exists(templatepath):
            response.status = (404, "Not Found")
            return "Page not found :C"
        
        if self.apiclass.authhook != None:
            response.set_header("Cache-Control", "no-cache")
            if (self.siteconf["pages"][pageindex]["require_auth"]) and (request.get_cookie("csg2sess") not in self.runningsessions):
                response.status = (307, "Not Logged In")
                return ""
        else:
            response.set_header("Cache-Control", "max-age=300")
        
        return butcheredbottle.template(os.path.join(self.themepath, "master.tpl"),
            title = self.siteconf["site"]["title"],
            link_elements = self.siteconf["pages"][pageindex]["link_elements"],
            nav_links = [("/" + k["navpath"], k["title"],) for k in self.siteconf["pages"] if ((k["position"] == "navbar") and ((k["require_auth"] == False) or ((k["require_auth"] == True) and (request.get_cookie("csg2sess") in self.runningsessions))))],
            cog_links = [("/" + k["navpath"], k["title"],) for k in self.siteconf["pages"] if ((k["position"] == "cog") and ((k["require_auth"] == False) or ((k["require_auth"] == True) and (request.get_cookie("csg2sess") in self.runningsessions))))],
            content = templatepath,
            csg2api = self.apiclass,
            is_authenticated = (request.get_cookie("csg2sess") in self.runningsessions),
            pathargs = tplargs
        })

    # Route: "/auth/login", method="POST"
    def dologin(self):
        response = self.apiclass.get_response()
        if self.apiclass.authhook == None:
            response.status = (303, "No Need To Log In")
            response.set_header("Location", "/")
            return ""
        if self.apiclass.authhook(request.forms.user, request.forms.password):
            uid = uuid.uuid4().hex + uuid.uuid4().hex
            response.set_cookie("csg2sess", uid, path="/", httponly=True)
            self.runningsessions[uid] = request.forms.user
            response.status = (303, "Successfully Logged In")
            response.set_header("Location", "/")
            return ""
        else:
            response.status = (303, "Incorrect Credentials")
            response.set_header("Location", "/")
            return ""

    # Route: "/auth/logout"
    def dologout(self):
        response = self.apiclass.get_response()
        if self.apiclass.authhook == None:
            response.status = (303, "No Need To Log Out")
            response.set_header("Location", "/")
            return ""
        else:
            del self.runningsessions[request.get_cookie("csg2sess")]
            response.delete_cookie("csg2sess", path="/", httponly=True)
            response.status = (303, "Successfully Logged Out")
            response.set_header("Location", "/")
            return ""
    
    def __call__(self, environ, start_response):
        """ WSGI interface """
        method = environ["REQUEST_METHOD"]
        path = os.path.join("/", environ["PATH_INFO"], environ["SCRIPT_NAME"]) # We only support POSIX, so...
        logging.info("{} {}".format(method, path))
        self.threadlocal["errout"] = environ["wsgi.errors"]
        self.threadlocal["httpinput"] = environ["wsgi.input"]
        self.threadlocal["wsgienviron"] = environ
        
        for definedroute in self.route_res:
            if definedroute[0] != method:
                continue
            reresult = definedroute[1][2].match(path)
            if reresult:
                callable_args = []
                callable_kwargs = {}
                for i in range(1, definedroute[1][0]+1):
                    callable_args.append(reresult.group(i))
                for k in definedroute[1][1]:
                    callable_kwargs[k] = reresult.group(k)
                
                callableresult = definedroute[2](*callable_args, **callable_kwargs)
                callableheaders = self.threadlocal["_httpresponseobj"].headers
                
                respheaders = [(key, callableheaders[key]) for key in callableheaders]
                callablecookies = self.threadlocal["_httpresponseobj"].cookies.output()
                for line in callablecookies.split('\r\n'):
                    for left,right in line.split(':', 1):
                        respheaders.append((left, right.lstrip()))
            
                callablestatus = self.threadlocal["_httpresponseobj"].status
                start_response("{} {}".format(status[0], status[1]), respheaders)
                return [callableresult]
