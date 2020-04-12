from flask import (
    render_template,
    url_for,
    make_response,
    redirect,
    flash,
    request,
    abort,
    jsonify,
)
from hat_game import app, db, id_generator
from hat_game.forms import GameJoinForm
from hat_game.models import Game, HatPick
from sqlalchemy.exc import IntegrityError
import json
import random

rand = random.SystemRandom()


@app.route("/")
@app.route("/index", strict_slashes=False)
def index():
    return render_template("index.html", title="Home")


def get_default_names():
    with open("hat_game/names.json", "r") as fd:
        data = json.load(fd)

    return [HatPick(name=datum, submitter="me") for datum in data["names"]]


@app.route("/games", methods=["POST"], strict_slashes=False)
def create_game():
    json_body = request.json
    if json_body and json_body["default"]:
        hat_picks = get_default_names()
    else:
        hat_picks = []

    for try_n in range(0, 10):
        try:
            game_id = id_generator.get_id()
            game = Game(game_id=game_id)
            for pick in hat_picks:
                game.hat_picks.append(pick)
            db.session.add(game)
            db.session.commit()
        except IntegrityError:
            game_id = None
            db.session.rollback()

    if game_id is None:
        abort(500, "Game creation failed")

    game_url = url_for("game_page", game_id=game_id)
    resp = make_response("", 201)
    resp.headers["Location"] = game_url
    return resp


@app.route("/game/<string:game_id>", strict_slashes=False)
def game_page(game_id):
    # TODO check for user session and redirect if not already playing.
    game = Game.query.filter_by(game_id=game_id).limit(1).first()
    if game is None:
        abort(404, "Game {game_id} not found")

    return render_template(
        "game.html",
        title="Game {game_id}",
        game_id=game.game_id,
        url_root=request.url_root[:-1],
    )


@app.route("/game/<string:game_id>/draw", methods=["POST"], strict_slashes=False)
def draw_name(game_id):
    names = (
        HatPick.query.filter_by(picked=False)
        .join(Game)
        .filter(Game.game_id == game_id)
        .all()
    )
    if len(names) == 0:
        return jsonify({"empty": True})

    drawn = rand.choice(names)
    drawn.picked = True
    # Write-back the chosen one
    db.session.commit()
    return jsonify({"name": drawn.name, "empty": False})


@app.route("/game/<string:game_id>/join", methods=["POST", "GET"], strict_slashes=False)
def join_game(game_id):
    game = Game.query.filter_by(game_id=game_id).limit(1).first()
    if game is None:
        abort(404, "Game {game_id} not found")

    # TODO check for user session and redirect if already playing.
    form = GameJoinForm()
    if form.validate_on_submit():
        flash("User {} joined game {}".format(form.username.data, game.game_id))
        game.hat_picks.extend([
            HatPick(name=form.names_0.data, submitter=form.username.data),
            HatPick(name=form.names_1.data, submitter=form.username.data),
            HatPick(name=form.names_2.data, submitter=form.username.data),
            HatPick(name=form.names_3.data, submitter=form.username.data),
        ])
        db.session.commit()
        return redirect("/game/{}".format(game.game_id))

    return render_template(
        "game_join_form.html",
        title="Join {game_id}",
        game_id=game.game_id,
        url_root=request.url_root[:-1],
        form=form,
    )
