import unittest, socket, threading, struct, subprocess, sys, os, time, urllib.request, urllib.error, json, http.cookiejar
from modbus import Gateway
class Protocol(unittest.TestCase):
    def serve(self, bad=False):
        sock=socket.socket();sock.bind(('127.0.0.1',0));sock.listen()
        port=sock.getsockname()[1]
        def run():
            with sock:
                c,_=sock.accept()
                with c:
                    req=b''
                    while len(req)<12:req+=c.recv(12-len(req))
                    tid,_,_,unit=struct.unpack('>HHHB',req[:7])
                    reply=struct.pack('>HHHB',tid+(1 if bad else 0),0,19,unit)+bytes([3,16])+struct.pack('>8H',650,40,0,0,0,0,30,0)
                    try:
                        for b in reply:c.sendall(bytes([b]))
                    except (BrokenPipeError, ConnectionResetError):pass
        t=threading.Thread(target=run);t.start();return port,t
    def test_fragmented_tcp(self):
        port,t=self.serve();self.assertEqual(Gateway('127.0.0.1',port).read(2)[1],40);t.join()
    def test_invalid_transaction(self):
        port,t=self.serve(True)
        with self.assertRaises(ValueError):Gateway('127.0.0.1',port).read(2)
        t.join()
class Web(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=subprocess.Popen([sys.executable,'server.py'],env={**os.environ,'FARM_MODE':'demo'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        cls.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        for _ in range(40):
            try:urllib.request.urlopen('http://127.0.0.1:8000');break
            except OSError:time.sleep(.1)
    @classmethod
    def tearDownClass(cls):cls.p.terminate();cls.p.wait()
    def request(self,path,data=None):
        req=urllib.request.Request('http://127.0.0.1:8000/api/'+path,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json'})
        try:
            with self.opener.open(req) as r:return r.status,json.load(r)
        except urllib.error.HTTPError as e:return e.code,json.load(e)
    def test_login_validation_control(self):
        self.assertEqual(self.request('state')[0],401)
        self.assertEqual(self.request('login',{'username':'smartfarm2026','password':'bad'})[0],401)
        self.assertEqual(self.request('login',{'username':'smartfarm2026','password':'smartfarm1234'})[0],200)
        self.assertEqual(self.request('state')[1]['mode'],'demo')
        self.assertEqual(self.request('control',{'unit':2,'address':4,'value':1})[0],200)
        self.assertEqual(self.request('control',{'unit':1,'address':4,'value':1})[0],400)
        self.assertEqual(self.request('control',{'unit':2,'address':6,'value':101})[0],400)
        time.sleep(12)
        self.assertEqual(self.request('state')[1]['nodes'][1]['registers'][4],0)
if __name__=='__main__':unittest.main()
