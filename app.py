from flask import Flask, render_template
import json

app = Flask(__name__)


@app.route("/")
def home():

    with open("data/nifty50.json", encoding="utf-8") as f:
        data = json.load(f)

    return render_template(
        "index.html",
        rows=data["companies"],
        updated=data["updated"],
        count=data["count"],
    )


if __name__ == "__main__":
    app.run(debug=True)
