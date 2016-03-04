#!/usr/bin/env python3
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
from bottle import route, run, static_file, HTTPResponse, view, response, default_app
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

argparser = argparse.ArgumentParser()
argparser.add_argument('sitesfolder', metavar='<site storage folder>', help="path to the folder containing sites")
argparser.add_argument('siteroot', metavar='<site name>', help="site name/the folder with config.json")
parsedargs = argparser.parse_args()

if "CSG2_THEMES" not in os.environ:
    print("/!\\ CSG2_THEMES is not defined. Please launch through the wrapper script.", file=sys.stderr)
    exit(1)
if "CSG2_SITECONF" not in os.environ:
    print("/!\\ CSG2_SITECONF is not defined. Please launch through the wrapper script.", file=sys.stderr)
    exit(1)

sitepath = os.path.abspath(os.path.join(parsedargs.sitesfolder, parsedargs.siteroot))
siteconffile = open(os.path.join(sitepath, "config.json"), mode="rt", encoding="utf-8")
siteconf = json.load(siteconffile)
siteconffile.close()

themesroot = os.path.abspath(os.environ["CSG2_THEMES"])
themepath = os.path.join(themesroot, siteconf["site"]["theme"])
os.chdir(sitepath)

runningsessions = []
apiclass = sandbox.csg2api(default_app())

if "additional_code" in siteconf["site"]:
    oldpath = sys.path
    sys.path[0] = sitepath
    importlib.invalidate_caches()
    with open(os.path.join(sitepath, siteconf["site"]["additional_code"]), mode="rt") as codefile:
        sandbox.create_box(codefile.read(), default_app(), apiclass=apiclass) # This file is excempt from the linking clauses in the license, allowing it to be non-(A)GPL.
    sys.path = oldpath
    importlib.invalidate_caches()

if "domain_name" not in siteconf["site"]:
    siteconf["site"]["domain_name"] = parsedargs.siteroot.replace("/", "_")

@route("/rand/<filepath:path>")
def getrandstaticredirect(filepath):
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
        matches = matches + glob.glob(os.path.join(sitepath, "static/", modfilepathstr))
    if len(matches) == 0:
        response.status = 404
        return "Files not found."
    pick = random.choice(matches).replace(sitepath, "").replace("\\", "/")
    response.set_header("Location", pick)
    return ""

@route("/static/<filepath:path>")
def getstatic(filepath):
    response.set_header("Cache-Control", "max-age=3600")
    return static_file(filepath, root=os.path.join(sitepath, "static/"))

@route("/sass/master.scss")
def compilethemesass():
    output = ""
    response.set_header("Cache-Control", "max-age=3600")
    response.content_type = "text/css"
    with open(os.path.join(sitepath, "scss/theme.scss"), mode="rt") as fl:
        output += fl.read()
    with open(os.path.join(themepath, "master.scss"), mode="rt") as fl:
        output += fl.read()
    return sass.compile(string=output)

@route("/sass/<filename:re:.*\.scss>")
def compilesass(filename):
    output = ""
    response.set_header("Cache-Control", "max-age=3600")
    response.content_type = "text/css"
    if not os.path.exists(os.path.join(sitepath, "scss/" + filename)):
        response.status = 404
        return "SCSS file not found."
    with open(os.path.join(sitepath, "scss/" + filename), mode="rt") as fl:
        output += fl.read()
    return sass.compile(string=output)

@route("/")
@route("/<filepath:path>")
@view(os.path.join(themepath, "master.tpl"))
def catchall(filepath="index"):
    if apiclass.authhook != None:
        response.set_header("Cache-Control", "no-cache")
        if (request.get_cookie("csg2sess") not in runningsessions) and (filepath != "login"):
            response.status = "307 Not Logged In"
            response.set_header("Location", "/login")
            return ""
    else:
        response.set_header("Cache-Control", "max-age=3600")
    if filepath[-1] == "/":
        filepath = filepath[:-1]
    pageindex = -1
    for i in range(0, len(siteconf["pages"])-1):
        if siteconf["pages"][i]["path"] == filepath:
            pageindex = i
            break
    if not os.path.exists(os.path.join(sitepath, filepath + ".tpl")):
        response.status = 404
        return "Page not found :C"
    return {
        "title": siteconf["site"]["title"],
        "link_elements": siteconf["pages"][pageindex]["link_elements"],
        "nav_links": [("/" + k["path"], k["title"],) for k in siteconf["pages"]],
        "content": os.path.join(sitepath, filepath + ".tpl")
    }

@route("/login", method="POST")
def dologin():
    if apiclass.authhook == None:
        response.status = "303 No Need To Log In"
        response.set_header("Location", "/")
        return ""
    if apiclass.authhook(request.forms.user, request.forms.password):
        uid = uuid.uuid4().hex + uuid.uuid4().hex
        response.set_cookie("csg2sess", uid)
        runningsessions.append(uid)
        response.status = "303 Successfully Logged In"
        response.set_header("Location", "/")
        return ""
    else:
        response.status = "303 Incorrect Credentials"
        response.set_header("Location", "/login")
        return ""

from waitress import serve as waitress_serve
socketpath = "/tmp/csg2_{}.sock".format(siteconf["site"]["domain_name"].replace(".", "_"))
print("-> Generating config.")
with open(os.path.abspath(os.environ["CSG2_SITECONF"]), mode="rt", encoding="utf-8") as sitetemplate:
    sitetemplatetxt = sitetemplate.read()
    newsite = sitetemplatetxt.replace("%%SERVERNAME%%", siteconf["site"]["domain_name"]).replace("%%SOCKETPATH%%", socketpath)
    with open("/tmp/{}.csg2nginx".format(siteconf["site"]["domain_name"].replace(".", "_")), mode="wt", encoding="utf-8") as newconf:
        newconf.write(newsite)
print("-> Serving up site on '{}'.".format(socketpath))
waitress_serve(default_app(), unix_socket=socketpath)
