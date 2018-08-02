from UPlusDataManager import UPlusDataManager
from flask import Flask, request
from queue import Queue
import time
import threading


app = Flask(__name__)
manager = UPlusDataManager()
queue = Queue()

def process():
    while True:
        manager = UPlusDataManager()
        manager.login("cd2love@hanmail.net", "aldud1010!")
        manager.send_data("010-7469-9464", "010-3469-9464", "1024")

        time.sleep(60 + 10)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/share", methods=["POST"])
def share():
    print(request.form)
    language = request.form.get('language')
    return None

if __name__ == '__main__':
    t = threading.Thread(target=process)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
