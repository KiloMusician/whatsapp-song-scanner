path = '/home/xeno/whatsapp-song-scanner/src/radiodj_integration/radiodj_client.py'
with open(path) as f:
    src = f.read()

old = (
    '                response = requests.get(f"{self.api_url}/health", timeout=5)\n'
    '                status["api_available"] = response.status_code == 200'
)
new = (
    '                response = requests.get(\n'
    '                    f"{self.api_url}/opt",\n'
    '                    params={"auth": self.api_key, "command": "Status"},\n'
    '                    timeout=5,\n'
    '                )\n'
    '                status["api_available"] = response.status_code == 200'
)

if old in src:
    with open(path, 'w') as f:
        f.write(src.replace(old, new, 1))
    print('PATCHED')
else:
    print('NOT FOUND - snippet:')
    idx = src.find('/health')
    print(repr(src[max(0,idx-100):idx+100]))
