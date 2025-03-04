from flask import jsonify, render_template
from app import app, mongo

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/page1")
def page1():
    return render_template("page1.html")

@app.route("/page2")
def page2():
    return render_template("page2.html")

@app.route("/page3")
def page3():
    return render_template("page3.html")

@app.route("/page4")
def page4():
    return render_template("page4.html")

@app.route("/lost_items", methods=["GET"])
def get_lost_items():
    try:
        items_collection = mongo.db.item
        lost_items = list(items_collection.find({"status": "lost"}))

        for item in lost_items:
            item["_id"] = str(item["_id"])
        return jsonify(lost_items)
    except Exception as e:
        print(f"Error accessing MongoDB: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/found_items", methods=["GET"])
def get_found_items():
    try:
        items_collection = mongo.db.item
        found_items = list(items_collection.find({"status": "lost"}))

        for item in found_items:
            item["_id"] = str(item["_id"])
        return jsonify(found_items)
    except Exception as e:
        print(f"Error accessing MongoDB: {e}")
        return jsonify({"error": "Database error"}), 500