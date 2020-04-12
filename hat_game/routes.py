from flask import render_template, url_for, make_response, redirect, flash, request
from hat_game import app, id_generator
from hat_game.forms import GameJoinForm


@app.route("/")
@app.route("/index", strict_slashes=False)
def index():
    return render_template("index.html", title="Home")


@app.route("/games", methods=["POST"], strict_slashes=False)
def create_game():
    game_id = id_generator.get_id()
    # Check it doesn't conflict with existing game.
    game_url = url_for("game_page", game_id=game_id)
    resp = make_response("", 201)
    resp.headers["Location"] = game_url
    return resp


@app.route("/game/<string:game_id>", methods=["POST", "GET"], strict_slashes=False)
def game_page(game_id):
    # TODO validate game_id.
    # TODO check for user session and redirect if not already playing.
    return render_template(
        "game.html",
        title="Game {game_id}",
        game_id=game_id,
        url_root=request.url_root[:-1],
    )


@app.route("/game/<string:game_id>/join", methods=["POST", "GET"], strict_slashes=False)
def join_game(game_id):
    # TODO validate game_id.
    # TODO check for user session and redirect if already playing.
    form = GameJoinForm()
    if form.validate_on_submit():
        flash("User {} joined game {}".format(form.username.data, game_id))
        # TODO write user picks into DB.
        return redirect("/game/{}".format(game_id))

    return render_template(
        "game_join_form.html",
        title="Join {game_id}",
        game_id=game_id,
        url_root=request.url_root[:-1],
        form=form,
    )
