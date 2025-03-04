from flask import jsonify, render_template, request, redirect, url_for, session, flash
from bson.objectid import ObjectId
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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]  # Get email from form
        password = request.form["password"]  # Get password from form

        # Look for the user in the MongoDB 'user' collection
        user = mongo.db.user.find_one({"email": email})

        if user and user["password"] == password:  
            session["user_id"] = str(user["_id"])  # Store user session
            return redirect(url_for("home"))  # Redirect to home page
        
        else:
            flash("Invalid email or password. Please try again.")

    return render_template("login.html")  # Render login page

@app.route("/account")
def account():
    try:
        # Ensure user is logged in
        user_id = session.get("user_id")

        user = mongo.db.user.find_one({"_id": ObjectId(user_id)})

        if not user:
            flash("User not found.")
            return redirect(url_for("login"))

        user_posts = list(mongo.db.item.find({"userId": str(user["_id"])}).sort("dateLost", -1))

        return render_template("account.html", user=user, user_posts=user_posts)

    except Exception as e:
        print(f"Error accessing account data: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/lost_items", methods=["GET"])
def lost_items():
    try:
        items_collection = mongo.db.item
        query = request.args.get("query", "").strip() # get search query

        search = {"status": "lost"}

        # If we have a nonempty search
        if query:
            search["$or"] = [
                {"itemName": {"$regex": query, "$options": "i"}}, 
                {"description": {"$regex": query, "$options": "i"}}
            ]

        lost_items = list(items_collection.find(search).sort("dateLost", -1))

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
        query = request.args.get("query", "").strip() # get search query

        search = {"status": "found"}

         # If we have a nonempty search
        if query:
            search["$or"] = [
                {"itemName": {"$regex": query, "$options": "i"}}, 
                {"description": {"$regex": query, "$options": "i"}}
            ]

        found_items = list(items_collection.find(search).sort("dateFound", -1))

        for item in found_items:
            item["_id"] = str(item["_id"])

        return render_template("found_items.html", found_items=found_items)

    except Exception as e:
        print(f"Error accessing MongoDB: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/submit_post", methods=["POST"])
def submit_post():
    try:
        itemName = request.form["itemName"]
        description = request.form["description"]
        status = request.form["status"]
        location = int(request.form["location"])
        date = request.form["date"]

        if status == 'found':
            item = {
                "itemName": itemName,
                "description": description,
                "status": status,
                "floor": location,
                "dateFound": date,
                "updatedAt": date
            }
            mongo.db.item.insert_one(item)
            
        else:
            item = {
                "itemName": itemName,
                "description": description,
                "status": status,
                "floor": location,
                "dateLost": date,
                "updatedAt": date
            }
            mongo.db.item.insert_one(item)

        print("Item posted successfully!", "success")
        return redirect(url_for("home"))

    except Exception as e:
        print(f"Error submitting post: {e}")
        return redirect(url_for("post_item"))

if __name__ == '__main__':
    app.run(debug=True)