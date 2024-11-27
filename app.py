# app.py
from flask import Flask, render_template, request, jsonify
from chat import get_response, get_suggestions
import json

app = Flask(__name__)

@app.get("/")
def index_get():
    return render_template("base.html")

@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response, options = get_response(text)
    message = {"answer": response, "options": options}
    return jsonify(message)

@app.route("/suggestions")
def suggestions():
    suggestions = get_suggestions()
    return jsonify(suggestions)

if __name__ == "__main__":
    app.run(debug=True)
