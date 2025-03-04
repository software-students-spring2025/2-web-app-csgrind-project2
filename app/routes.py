from flask import jsonify, render_template, request, redirect, url_for
from app import app, mongo

@app.route("/")
def home():
    try:
        items_collection = mongo.db.item

        lost_items = list(items_collection.find({"status": "lost"}).sort("dateLost", -1).limit(5))
        found_items = list(items_collection.find({"status": "found"}).sort("dateFound", -1).limit(5))

        for item in lost_items + found_items:
            item["_id"] = str(item["_id"])

        recent_items = lost_items + found_items
        recent_items.sort(key=lambda x: x.get("dateLost", x.get("dateFound")), reverse=True)

        return render_template("index.html", recent_items=recent_items[:3])

    except Exception as e:
        print(f"Error fetching recent items: {e}")
        return render_template("index.html", recent_items=[])

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

@app.route("/lost_items", methods=["GET"])
def lost_items():
    try:
        items_collection = mongo.db.item
        lost_items = list(items_collection.find({"status": "lost"}).sort("dateLost", -1))

        for item in lost_items:
            item["_id"] = str(item["_id"])
        return render_template("lost_items.html", lost_items=lost_items)

    except Exception as e:
        print(f"Error accessing MongoDB: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/found_items", methods=["GET"])
def found_items():
    try:
        items_collection = mongo.db.item
        found_items = list(items_collection.find({"status": "found"}).sort("dateFound", -1))

        for item in found_items:
            item["_id"] = str(item["_id"])
        return render_template("found_items.html", found_items=found_items)
    except Exception as e:
        print(f"Error accessing MongoDB: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/submit_post", methods=["POST"])
def submit_post():
    try:
        item_name = request.form["item_name"]
        description = request.form["description"]
        status = request.form["status"]
        location = request.form["location"]
        date = request.form["date"]

        if status == 'found':
            item = {
                "item_name": item_name,
                "description": description,
                "status": status,
                "floor": location,
                "dateFound": date
            }
            mongo.db.item.insert_one(item)
        else:
            item = {
                "item_name": item_name,
                "description": description,
                "status": status,
                "floor": location,
                "dateLost": date
            }
            mongo.db.item.insert_one(item)

        print("Item posted successfully!", "success")
        return redirect(url_for("home"))

    except Exception as e:
        print(f"Error submitting post: {e}")
        return redirect(url_for("post_item"))

if __name__ == '__main__':
    app.run(debug=True)