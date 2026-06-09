from flask import Flask, jsonify
import json

app = Flask(__name__)

log_file = "logs.json"

def load_logs():
    events = []
    try: 
        with open(log_file, "r") as f:
            for line in f :
                try :
                    events.append(json.loads(line))
                except:
                    continue
    except FileNotFoundError:
        pass
    
    return events[-100:]


@app.route("/events")

def events():
    return jsonify(load_logs())

@app.route("/")
def home():
    return open("templates/dashboard.html").read()

if __name__== "__main__":
    app.run(debug=True, port=5000)