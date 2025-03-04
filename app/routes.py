from flask import jsonify, render_template
from app import app, mongo

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/lost_items")
def lost_items():
    return render_template("lost_items.html")

@app.route("/found_items")
def found_items():
    return render_template("found_items.html")

@app.route("/post_item")
def post_item():
    return render_template("post_item.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/account")
def account():
    return render_template("account.html")

@app.route("/api/lost_items", methods=["GET"])
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

@app.route("/api/found_items", methods=["GET"])
def get_found_items():
    try:
        items_collection = mongo.db.item
        found_items = list(items_collection.find({"status": "found"}))

        for item in found_items:
            item["_id"] = str(item["_id"])
        return jsonify(found_items)
    except Exception as e:
        print(f"Error accessing MongoDB: {e}")
        return jsonify({"error": "Database error"}), 500

if __name__ == '__main__':
    app.run(debug=True)