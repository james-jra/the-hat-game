from flask import render_template, url_for, make_response
from hat_game import app, id_generator


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Home")


@app.route("/game/<string:game_id>")
def game_page(game_id):
    return render_template(
        "game.html", title="Game {}".format(game_id), game_id=game_id
    )


@app.route("/games", methods=["POST"])
def create_game():
    game_id = id_generator.get_id()
    # Check it doesn't conflict with existing game.
    game_url = url_for("game_page", game_id=game_id)
    resp = make_response("", 201)
    resp.headers["Location"] = game_url
    return resp
