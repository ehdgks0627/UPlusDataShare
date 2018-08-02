from UPlusDataManager import UPlusDataManager
from flask import Flask, request, render_template, Response
from queue import Queue
from account import uplus_id, uplus_pw
import time
import threading


app = Flask(__name__)
manager = UPlusDataManager()
queue = Queue()
auth_dict = {}

def process():
    global queue
    manager = UPlusDataManager()

    while True:
        info = queue.get()
        if not info.get("send_req_auth"):
            manager.login(uplus_id, uplus_pw)
            manager.auth_req_sms(info.get("sender"))
            info["send_req_auth"] = True
            queue.put(info)
            time.sleep(1)
            continue

        if info.get("sender") not in auth_dict or len(auth_dict[info.get("sender")]) == 0:
            queue.put(info)
            time.sleep(1)
            continue
        manager.auth_sms(info.get("sender"), auth_dict[info.get("sender")].pop(-1))
        manager.gift(info.get("sender"), info.get("receiver"), info.get("cnt"))
        time.sleep(60 + 10)

def validate(info):
    if "sender" not in info:
        return False
    if "receiver" not in info:
        return False
    if "cnt" not in info:
        return False
    try:
        int(info.get("cnt"))
    except ValueError:
        return False
    return True

@app.route("/", methods=["GET"])
def index():
    global auth_dict
    return render_template("index.html")

@app.route("/share", methods=["POST"])
def share():
    global queue
    info = request.form.to_dict()
    if validate(info):
        info["send_req_auth"] = False
        queue.put(info)
    return Response()

@app.route("/auth", methods=["POST"])
def auth():
    global auth_dict
    sender = request.form.get("sender")
    if sender not in auth_dict:
        auth_dict[sender] = []
    auth_dict[sender].append(request.form.get("code"))
    return Response()

if __name__ == '__main__':
    t = threading.Thread(target=process)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=8000)
    # app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
