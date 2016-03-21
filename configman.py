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
import sys

defined_versions = [2, 3]
dropped_versions = [1]

def normalize_config(conf, siteroot):
    if "version" not in conf:
        print("Error: Version not defined in config!", file=sys.stderr)
        exit(101)
    if conf["version"] in dropped_versions:
        print("Error: Config version {} is no longer supported.".format(conf["version"]), file=sys.stderr)
        print("Error: Earliest supported version is {}.".format(defined_versions[0]), file=sys.stderr)
        exit(103)
    if conf["version"] not in defined_versions:
        print("Error: Config version {} not defined.".format(conf["version"]), file=sys.stderr)
        exit(102)
    if conf["version"] == defined_versions[-1]:
        return conf
    
    for ver in defined_versions:
        if ver <= conf["version"]:
            continue
        if ver == 2: # Bring up to spec with Version 2
            for pagekey in range(0, len(conf["pages"])):
                conf["pages"][pagekey]["hidden"] = False
                conf["pages"][pagekey]["require_auth"] = False
                print("Warning: With implicit upgrade to config version 2, page authentication was disabled.", file=sys.stderr)
        elif ver == 3: # Bring up to spec with Version 3
            for pagekey in range(0, len(conf["pages"])):
                conf["pages"][pagekey]["navpath"] = conf["pages"][pagekey]["path"]
                conf["pages"][pagekey]["path"] = conf["pages"][pagekey]["path"] + ".tpl"
                if conf["pages"][pagekey]["hidden"]:
                    conf["pages"][pagekey]["position"] = "hidden"
                else:
                    conf["pages"][pagekey]["position"] = "navbar"
    
    return conf
