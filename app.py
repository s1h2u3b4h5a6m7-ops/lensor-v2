# app.py
from flask import Flask, render_template

app = Flask(__name__)

DATA = [
    {"name": "Alpha", "status": "Ready", "value": 10},
    {"name": "Beta", "status": "Pending", "value": 20},
    {"name": "Gamma", "status": "Done", "value": 30},
]

@app.route("/")
def home():
    return render_template("index.html", rows=DATA)

if __name__ == "__main__":
    app.run(debug=True)
