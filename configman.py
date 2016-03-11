defined_versions = [1, 2]

def normalize_config(conf, siteroot, themeroot):
    if "version" not in conf:
        print("Error: Version not defined in config!")
        exit(101)
    if conf["version"] not in defined_versions:
        print("Error: Config version {} not defined.".format(conf["version"]))
        exit(102)
    if conf["version"] == defined_versions[-1]:
        return conf
    
    for ver in defined_versions:
        if ver < conf["version"]:
            continue
        if ver == 1: # Bring up to spec with Version 1
            if "domain_name" not in conf["site"]:
                conf["site"]["domain_name"] = siteroot.replace("/", "_")
        elif ver == 2: # Bring up to spec with Version 2
            for pagekey in range(0, len(conf["pages"])-1):
                conf["pages"][pagekey]["hidden"] = False
                conf["pages"][pagekey]["require_auth"] = False
    
    return conf
