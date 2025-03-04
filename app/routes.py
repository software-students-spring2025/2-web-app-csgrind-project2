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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form["firstName"]
        last_name = request.form["lastName"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        # Check if the user email already has a registered account
        existing_user = mongo.db.user.find_one({"email": email})
        if existing_user:
            flash("Email already registered. Please log in.")
            return redirect(url_for("login"))

        # If the user does not exist, insert the new user
        mongo.db.user.insert_one({
            "email": email,
            "password": password, 
            "firstName": first_name,
            "lastName": last_name,
            "role": role
        })
        
        flash("Account created successfully! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]  # Get email from form
        password = request.form["password"]  # Get password from form

        # Look for the user in the MongoDB 'user' collection
        user = mongo.db.user.find_one({"email": email})

        if user and user["password"] == password:  
            session["user_id"] = str(user["_id"])  # user session
            session["role"] = user["role"]         # role for use in editing/updating privileges
            return redirect(url_for("home"))  # Redirect to home page
        
        else:
            flash("Invalid email or password. Please try again.")

    return render_template("login.html")  # Render login page

@app.route("/account")
def account():
    try:
        # Ensure user is logged in
        user_id = session.get("user_id")

        if not user_id:
            flash("You must be logged in to access your account.", "error")
            return redirect(url_for("login"))

        user = mongo.db.user.find_one({"_id": ObjectId(user_id)})

        if not user:
            flash("User not found.", "error")
            return redirect(url_for("login"))

        user_posts = list(mongo.db.item.find({"userId": str(user["_id"])}).sort("dateLost", -1))

        for post in user_posts:
            post["_id"] = str(post["_id"])

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
        # Check if user is logged in
        user_id = session.get("user_id")
        if not user_id:
            flash("You must be logged in to post an item.", "error")
            return redirect(url_for("login"))

        itemName = request.form["itemName"]
        description = request.form["description"]
        status = request.form["status"]
        location = int(request.form["location"])
        date = request.form["date"]

        if status == 'found':
            item = {
                "userId": user_id,
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
                "userId": user_id,
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

@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    try:
        # Check if user is logged in
        user_id = session.get("user_id")
        user_role = session.get("role")

        items_collection = mongo.db.item
        post = items_collection.find_one({"_id": ObjectId(post_id)})

        if not post:
            flash("No posts created.", "error")
            return redirect(url_for("home"))

        # Admin or post owner can edit
        if user_role != "admin" and str(post["userId"]) != user_id:
            flash("You do not have permission to edit this post.", "error")
            return redirect(url_for("home"))

        if request.method == "POST":
            post["itemName"] = request.form["itemName"]
            post["description"] = request.form["description"]
            post["floor"] = int(request.form["location"])
            post["updatedAt"] = request.form["date"]

            items_collection.update_one({"_id": ObjectId(post_id)}, {"$set": post})

            flash("Post updated successfully!", "success")
            return redirect(url_for("home"))

        return render_template("edit_post.html", post=post)

    except Exception as e:
        print(f"Error updating post: {e}")
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for("home"))

@app.route("/delete_post/<post_id>", methods=["POST"])
def delete_post(post_id):
    try:
        # Ensure user is logged in
        user_id = session.get("user_id")
        user_role = session.get("role")

        if not user_id:
            flash("You must be logged in to delete a post.", "error")
            return redirect(url_for("login"))

        # Find the post
        post = mongo.db.item.find_one({"_id": ObjectId(post_id)})
        if not post:
            flash("Post not found.", "error")
            return redirect(url_for("home"))

        # Ensure user has the right to delete
        if user_role != "admin" and str(post["userId"]) != user_id:
            flash("You do not have permission to delete this post.", "error")
            return redirect(url_for("home"))

        # Delete the post
        mongo.db.item.delete_one({"_id": ObjectId(post_id)})

        flash("Post deleted successfully!", "success")
        return redirect(url_for("home"))  # Redirect to account page after deletion

    except Exception as e:
        print(f"Error deleting post: {e}")
        flash("An error occurred while deleting the post.", "error")
        return redirect(url_for("home"))



if __name__ == '__main__':
    app.run(debug=True)