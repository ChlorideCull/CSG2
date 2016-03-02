@csg2api.auth
def authcheck(user, pw):
    return ((user == "boom") and (pw == "moob"))
