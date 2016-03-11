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
from bottle import Bottle, static_file, HTTPResponse, view, request, response
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
import sandbox
import configman

class CSG2Server:
    runningsessions = []
    
    def __init__(self, themedir, siteconftemplate):
        self.wsgiapp = Bottle()
        self.apiclass = sandbox.csg2api(self.wsgiapp)
        
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
        
        # Assign routes (done before the site code to allow overrides)
        # This is functionally equivalent of what the language does, but makes sure Bottle will call the right instance.
        self.getrandstaticredirect = self.wsgiapp.route("/rand/<filepath:path>")(self.getrandstaticredirect)
        self.getstatic = self.wsgiapp.route("/static/<filepath:path>")(self.getstatic)
        self.compilethemesass = self.wsgiapp.route("/theme/sass/master.scss")(self.compilethemesass)
        self.getthemeasset = self.wsgiapp.route("/theme/static/<filepath:path>")(self.getthemeasset)
        self.compilesass = self.wsgiapp.route("/sass/<filename:re:.*\.scss>")(self.compilesass)
        self.catchall = self.wsgiapp.route("/")(
            self.wsgiapp.route("/<filepath:path>")(
                view(os.path.join(self.themepath, "master.tpl"))(self.catchall)
            )
        )
        self.dologin = self.wsgiapp.route("/login", method="POST")(self.dologin)
        
        # If they have code, run it
        if "additional_code" in self.siteconf["site"]:
            oldpath = sys.path
            sys.path[0] = self.sitepath
            importlib.invalidate_caches()
            with open(os.path.join(self.sitepath, self.siteconf["site"]["additional_code"]), mode="rt") as codefile:
                sandbox.create_box(codefile.read(), self.wsgiapp, apiclass=self.apiclass) # This file is excempt from the linking clauses in the license, allowing it to be non-(A)GPL.
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
        waitress_serve(self.wsgiapp, unix_socket=socketpath)

    # Route: "/rand/<filepath:path>"
    def getrandstaticredirect(self, filepath):
        extmap = {
            "image": ["png", "jpg", "jpeg", "gif"] # Using "image" as extention allows matching with all image types
        }
        response.status = 307 # Temporary Redirect
        modfilepath = filepath.split(".")
        targetmap = modfilepath[-1:]
        matches = []
        if modfilepath[-1] in extmap.keys():
            targetmap = extmap[modfilepath[-1]]
        for ext in targetmap:
            modfilepathstr = ".".join(modfilepath[:-1] + ["*"] + [ext])
            matches = matches + glob.glob(os.path.join(self.sitepath, "static/", modfilepathstr))
        if len(matches) == 0:
            response.status = 404
            return "Files not found."
        pick = random.choice(matches).replace(self.sitepath, "").replace("\\", "/")
        response.set_header("Location", pick)
        return ""

    # Route: "/static/<filepath:path>"
    def getstatic(self, filepath):
        response.set_header("Cache-Control", "max-age=300")
        return static_file(filepath, root=os.path.join(self.sitepath, "static/"))

    # Route: "/theme/sass/master.scss"
    def compilethemesass(self):
        output = ""
        response.set_header("Cache-Control", "max-age=300")
        response.content_type = "text/css"
        with open(os.path.join(self.sitepath, "scss/theme.scss"), mode="rt") as fl:
            output += fl.read()
        with open(os.path.join(self.themepath, "master.scss"), mode="rt") as fl:
            output += fl.read()
        return sass.compile(string=output)
    
    # Route: "/theme/static/<filepath:path>"
    def getthemeasset(self, filepath):
        response.set_header("Cache-Control", "max-age=300")
        return static_file(filepath, root=os.path.join(self.themepath, "assets/"))

    # Route: "/sass/<filename:re:.*\.scss>"
    def compilesass(self, filename):
        output = ""
        response.set_header("Cache-Control", "max-age=300")
        response.content_type = "text/css"
        if not os.path.exists(os.path.join(self.sitepath, "scss/" + filename)):
            response.status = 404
            return "SCSS file not found."
        with open(os.path.join(self.sitepath, "scss/" + filename), mode="rt") as fl:
            output += fl.read()
        return sass.compile(string=output)

    # Route: "/"
    # Route: "/<filepath:path>"
    def catchall(self, filepath="index"):
        if filepath[-1] == "/":
            filepath = filepath[:-1]
        pageindex = -1
        for i in range(0, len(self.siteconf["pages"])-1):
            if self.siteconf["pages"][i]["path"] == filepath:
                pageindex = i
                break
        if not os.path.exists(os.path.join(self.sitepath, filepath + ".tpl")):
            response.status = 404
            return "Page not found :C"
        
        if self.apiclass.authhook != None:
            response.set_header("Cache-Control", "no-cache")
            if (self.siteconf["pages"][i]["require_auth"]) and (request.get_cookie("csg2sess") not in self.runningsessions) and (filepath != "login"):
                response.status = "307 Not Logged In"
                response.set_header("Location", "/login")
                return ""
        else:
            response.set_header("Cache-Control", "max-age=300")
        
        return {
            "title": self.siteconf["site"]["title"],
            "link_elements": self.siteconf["pages"][pageindex]["link_elements"],
            "nav_links": [("/" + k["path"], k["title"],) for k in self.siteconf["pages"]],
            "content": os.path.join(self.sitepath, filepath + ".tpl")
        }

    #Route: "/login", method="POST"
    def dologin(self):
        if self.apiclass.authhook == None:
            response.status = "303 No Need To Log In"
            response.set_header("Location", "/")
            return ""
        if self.apiclass.authhook(request.forms.user, request.forms.password):
            uid = uuid.uuid4().hex + uuid.uuid4().hex
            response.set_cookie("csg2sess", uid)
            self.runningsessions.append(uid)
            response.status = "303 Successfully Logged In"
            response.set_header("Location", "/")
            return ""
        else:
            response.status = "303 Incorrect Credentials"
            response.set_header("Location", "/login")
            return ""
