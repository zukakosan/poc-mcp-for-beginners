import requests

with requests.get('http://localhost:8000/stream', stream=True) as r:
    for line in r.iter_lines():
        if line:
            # flush=True は、print の出力を即座に表示するためのオプション
            print(line.decode('utf-8'), flush=True)