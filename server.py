from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def route_list():
    pass


@app.route("/question/<question_id>")
def route_question(question_id):
    pass


@app.route("/add-question")
def route_add():
    pass
