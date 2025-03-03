from flask import Blueprint, render_template

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/page1")
def page1():
    return render_template("page1.html")

@main.route("/page2")
def page2():
    return render_template("page2.html")

@main.route("/page3")
def page3():
    return render_template("page3.html")

@main.route("/page4")
def page4():
    return render_template("page4.html")
