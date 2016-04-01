import http.cookies

class HTTPRequest:
    def __init__(self, threadlocal):
        self.localdata=threadlocal
        
        self.headers = {}
        for key in self.localdata["wsgienviron"].keys():
            if key.startswith("HTTP_"):
                self.headers[key[5:]] = self.localdata["wsgienviron"][key]
        
        # Wrap input stream functions (see PEP-3333)
        self.read = self.localdata["httpinput"].read
        self.readline = self.localdata["httpinput"].readline
        self.readlines = self.localdata["httpinput"].readlines
        self.__iter__ = self.localdata["httpinput"].__iter__
    
    def get_header(self, headername):
        """
        Get a header from the HTTP request.
        """
        cgiheadername = headername.upper().replace("-", "_")
        if cgiheadername in self.headers:
            return self.headers[cgiheadername]
        else:
            return ""
            
    def get_cookies(self):
        return http.cookies.SimpleCookie(self.headers["COOKIE"])
        

class HTTPResponse:
    def __init__(self, threadlocal):
        self.localdata=threadlocal
        self.status = (200, "OK")
        self.headers = {}
        self.cookies = http.cookies.SimpleCookie()
        
    def set_status(self, code, text):
        self.status = (code, text)
    
    def set_header(self, headername, value):
        self.headers[headername] = value
