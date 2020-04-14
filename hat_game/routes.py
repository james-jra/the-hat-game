from datetime import datetime
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
import json
import random
from sqlalchemy.exc import IntegrityError

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
        abort(500, description="Game creation failed")

    game_url = url_for("game_page", game_id=game_id)
    resp = make_response("", 201)
    resp.headers["Location"] = game_url
    return resp


@app.route("/game/<string:game_id>", strict_slashes=False)
def game_page(game_id):
    # TODO check for user session and redirect if not already playing.
    game = Game.query.filter_by(game_id=game_id).limit(1).first()
    if game is None:
        abort(404, description="Game {game_id} not found")

    return render_template(
        "game.html",
        title="Game {game_id}",
        game_id=game.game_id,
        url_root=request.url_root[:-1],
    )


@app.route("/game/<string:game_id>/join", methods=["POST", "GET"], strict_slashes=False)
def join_game(game_id):
    game = Game.query.filter_by(game_id=game_id).limit(1).first()
    if game is None:
        abort(404, description="Game {game_id} not found")

    # TODO check for user session and redirect if already playing.
    form = GameJoinForm()
    if form.validate_on_submit():
        flash("User {} joined game {}".format(form.username.data, game.game_id))
        game.hat_picks.extend(
            [
                HatPick(name=form.names_0.data, submitter=form.username.data),
                HatPick(name=form.names_1.data, submitter=form.username.data),
                HatPick(name=form.names_2.data, submitter=form.username.data),
                HatPick(name=form.names_3.data, submitter=form.username.data),
            ]
        )
        db.session.commit()
        return redirect("/game/{}".format(game.game_id))

    return render_template(
        "game_join_form.html",
        title="Join {game_id}",
        game_id=game.game_id,
        url_root=request.url_root[:-1],
        form=form,
    )


@app.route("/game/<string:game_id>/hat_picks", strict_slashes=False)
def get_game_hat_picks(game_id):
    hat_picks = HatPick.query.join(Game).filter(Game.game_id == game_id).all()

    return jsonify([hat_pick.as_dict() for hat_pick in hat_picks])


@app.route(
    "/game/<string:game_id>/hat_picks/draw", methods=["POST"], strict_slashes=False
)
def draw_name(game_id):
    hat_picks = (
        HatPick.query.filter_by(picked=False)
        .join(Game)
        .filter(Game.game_id == game_id)
        .all()
    )
    if len(hat_picks) == 0:
        return jsonify(dict())

    hat_pick = rand.choice(hat_picks)
    hat_pick.picked = True
    # Write-back the chosen one
    db.session.commit()
    return jsonify({"hat_pick": hat_pick.as_dict()})


@app.route(
    "/game/<string:game_id>/hat_pick/<int:name_id>",
    methods=["PUT"],
    strict_slashes=False,
)
def update_name(game_id, name_id):
    hat_pick = HatPick.query.filter_by(id=name_id).one_or_none()
    if hat_pick is None:
        abort(404, description="Name {name_id} not found")

    if not request.json:
        abort(400, description="Request had no JSON body")
    if "name" in request.json and type(request.json["name"]) is not str:
        abort(400, description="name invalid")
    if "submitter" in request.json and type(request.json["submitter"]) is not str:
        abort(400, description="submitter invalid")
    if "picked" in request.json and type(request.json["picked"]) is not bool:
        abort(400, description="picked invalid")
    if "id" in request.json and type(request.json["id"]) is not int:
        abort(400, description="id invalid")
    if "game_id" in request.json and type(request.json["game_id"]) is not int:
        abort(400, description="game_id invalid")

    hat_pick.name = request.json.get("title", hat_pick.name)
    hat_pick.submitter = request.json.get("description", hat_pick.submitter)
    hat_pick.picked = request.json.get("done", hat_pick.picked)
    hat_pick.timestamp = datetime.utcnow()

    if hat_pick.id != request.json.get("id", hat_pick.id):
        db.session.rollback()
        abort(403, "id field is immutable")
    if hat_pick.game_id != request.json.get("game_id", hat_pick.game_id):
        db.session.rollback()
        abort(403, "game_id field is immutable")

    # Write-back the chosen one
    db.session.commit()

    return jsonify({"hat_pick": hat_pick.as_dict()})
