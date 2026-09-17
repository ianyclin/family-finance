# minimal CDP client (stdlib only) for newbie walkthrough screenshots at 400px
import json, socket, base64, os, struct, subprocess, time, urllib.request, sys
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
class WS:
    def __init__(self,url):
        assert url.startswith("ws://"); hp,path=url[5:].split("/",1)
        h,p=hp.split(":"); self.s=socket.create_connection((h,int(p)))
        key=base64.b64encode(os.urandom(16)).decode()
        self.s.send(f"GET /{path} HTTP/1.1\r\nHost: {hp}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n".encode())
        buf=b""
        while b"\r\n\r\n" not in buf: buf+=self.s.recv(4096)
        self.rest=buf.split(b"\r\n\r\n",1)[1]; self.id=0
    def _recvn(self,n):
        while len(self.rest)<n:
            d=self.s.recv(1<<20)
            if not d: raise EOFError
            self.rest+=d
        r=self.rest[:n]; self.rest=self.rest[n:]; return r
    def send(self,obj):
        data=json.dumps(obj).encode(); hdr=bytearray([0x81]); L=len(data)
        if L<126: hdr.append(0x80|L)
        elif L<65536: hdr.append(0x80|126); hdr+=struct.pack(">H",L)
        else: hdr.append(0x80|127); hdr+=struct.pack(">Q",L)
        m=os.urandom(4); hdr+=m
        self.s.sendall(bytes(hdr)+bytes(b^m[i%4] for i,b in enumerate(data)))
    def recv(self):
        msg=b""
        while True:
            b0,b1=self._recvn(2); L=b1&0x7f
            if L==126: L=struct.unpack(">H",self._recvn(2))[0]
            elif L==127: L=struct.unpack(">Q",self._recvn(8))[0]
            msg+=self._recvn(L)
            if b0&0x80: return json.loads(msg)
    def call(self,method,**params):
        self.id+=1; i=self.id; self.send({"id":i,"method":method,"params":params})
        while True:
            r=self.recv()
            if r.get("id")==i:
                if "error" in r: raise RuntimeError(r["error"])
                return r["result"]
def start(port=9444):
    prof="/private/tmp/claude-501/-Users-linyenchu-Cladue-Code/f330c746-4fb1-4319-8da3-61dfb142160e/scratchpad/chrome-prof6"
    p=subprocess.Popen([CHROME,"--headless=new",f"--remote-debugging-port={port}",f"--user-data-dir={prof}","--no-first-run","--hide-scrollbars","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for _ in range(50):
        try:
            tabs=json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json")); break
        except Exception: time.sleep(0.2)
    t=[t for t in tabs if t["type"]=="page"][0]
    ws=WS(t["webSocketDebuggerUrl"])
    return p,ws
def ev(ws,expr):
    r=ws.call("Runtime.evaluate",expression=expr,returnByValue=True,awaitPromise=True)
    if "exceptionDetails" in r: raise RuntimeError(r["exceptionDetails"])
    return r["result"].get("value")
def shot(ws,path,clip=None):
    time.sleep(0.4)
    kw=dict(format="png")
    if clip: kw["clip"]=clip; kw["captureBeyondViewport"]=True
    d=ws.call("Page.captureScreenshot",**kw)["data"]
    open(path,"wb").write(base64.b64decode(d))
def load(ws,url,wait=2.5):
    ws.call("Page.enable"); ws.call("Page.navigate",url=url); time.sleep(wait)
