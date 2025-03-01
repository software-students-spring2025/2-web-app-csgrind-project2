from flask import Blueprint, render_template

#create a Blueprint called main
main = Blueprint("main", __name__)

#defines '/' as the index.html html file
@main.route("/")
def home():
    return render_template("index.html")

#login, method POST
@main.route("/login", methods=["POST"])
def login():
    pass

### -------------- Student Route -------------- ###

#student: post lost item, method POST
@main.route("/lost_items", methods=["POST"])
def post_lost_item():
    pass

#student: search for lost item, method GET
@main.route("/search", methods=["GET"])
def search_lost_item():
    pass

#student: upload picture to lost item, method POST
@main.route("/lost_items/upload_picture", methods=["POST"])
def upload_picture():
    pass

### -------------- Security Officer Route -------------- ###

#security officer: post found item, method POST
@main.route("/found_items", methods=["POST"])
def post_found_item():
    pass

#security officer: update item post, method PUT
@main.route("/found_items/<item_id>", methods=["PUT"])
def update_item_post(item_id):
    pass

#security officer: mark item as recovered, method DELETE
@main.route("/found_items/<item_id>", methods=["DELETE"])
def mark_item_recovered(item_id):
    pass

#security officer: view lost items, method GET
@main.route("/lost_items/all", methods=["GET"])
def view_lost_items():
    pass

#security officer: restrict access
@main.route("/restrict-access", methods=["GET"])
def restrict_access():
    pass