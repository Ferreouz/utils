#!/usr/bin/env python3

import re
import requests as r
import platform
from subprocess import run  

NODE_URL = "https://nodejs.org/dist/latest/"

def get_node_types():
    res = r.get(NODE_URL)
    text = res.text
    matches = re.findall("<a\s*href=\"(.*)\"", text)
    return '|' + '|'.join(matches) + '|' 

def get_cpu_type():
    cpu = platform.uname().machine
    out = cpu
    match cpu:
        case "x86_64":
            out = "x64"
        
        case "aarch64_be":
            out = "arm64"
        case "aarch64":
            out = "arm64"
        case "armv8b":
            out = "arm64"
        case "armv8l":
            out = "arm64"
        
        case "i386":
            out = "x86"
        case "i686":
            out = "x86"
    return out

def download_tar(version, cpu):
    url = NODE_URL + "node-v%s-linux-%s.tar.gz" % (version, cpu) 
    
    res = r.get(url)
    if "html" in res.headers['content-type'] or res.status_code != 200:
        return False

    with open('node.tar.gz', 'wb') as f:
        f.write(res.content)
    
    return True
def mk_script():
    content = """
#!/usr/bin/env bash

tar -zxf node.tar.gz --one-top-level=temp.node --strip-components 1
cd temp.node/
echo "[INFO] you will be prompted for your password"
sudo mv bin/* /usr/bin/
sudo mv lib/node_modules /usr/lib/
sudo npm i -g pm2 > /dev/null

echo "[+] Node, NPM and PM2 installed successfully"
echo "[INFO] eliminating temp files..."
cd .. && rm -rf temp.node; rm node.tar.gz; rm install-node.sh 
echo "[+] Done."
echo "Node version: "; node -v && echo "NPM version: "; npm -v  
"""
    with open('install-node.sh', 'w') as f:
        f.write(content)

def call_script():
    run(["/usr/bin/sh", "install-node.sh"])
    return None


cpu = get_cpu_type()
nodes = get_node_types()

match = re.findall("\|node-v([0-9\.]+)-linux-" + cpu + "\.tar.gz\|" ,nodes)
if not match:
    print("[-] Node for this architecture was not found.")
    exit()

if not download_tar(match[0], cpu):
    print("[-] Error occurred while downloading the zipped file.")
    exit()

mk_script()
call_script()
