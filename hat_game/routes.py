from datetime import datetime
from flask import (
    abort,
    flash,
    jsonify,
    make_response,
    redirect,
    request,
    render_template,
    session,
    url_for,
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


@app.route("/games", methods=["GET"], strict_slashes=False)
def list_games():
    games = Game.query.all()
    return jsonify([game.as_dict() for game in games])


def get_default_names():
    with open("hat_game/names.json", "r") as fd:
        data = json.load(fd)

    return [HatPick(name=datum, submitter="me") for datum in data["names"]]


@app.route("/games", methods=["POST"], strict_slashes=False)
def create_game():
    json_body = request.json
    if json_body and json_body.get("default", None):
        hat_picks = get_default_names()
    else:
        hat_picks = []

    if json_body and json_body.get("n_picks", None):
        n_picks = json_body.get("n_picks", None)
    else:
        n_picks = 4

    for try_n in range(0, 20):
        try:
            game_id = id_generator.get_id()
            game = Game(game_id=game_id, n_picks=n_picks)
            for pick in hat_picks:
                game.hat_picks.append(pick)
            db.session.add(game)
            db.session.commit()
        except IntegrityError:
            game_id = None
            db.session.rollback()

    if game_id is None:
        app.logger.error("Failed to generate game ID")
        abort(500, description="Game creation failed")

    game_url = url_for("game_page", game_id=game_id)
    resp = make_response("", 201)
    resp.headers["Location"] = game_url
    return resp


@app.route("/game/<string:game_id>", strict_slashes=False)
def game_page(game_id):
    game = Game.query.filter_by(game_id=game_id).limit(1).first()
    if game is None:
        abort(404, description=f"Game {game_id} not found")

    if game_id not in session.get("active_games", []):
        return redirect(url_for("join_game", game_id=game_id))

    return render_template(
        "game.html",
        title=f"Game {game_id}",
        game_id=game.game_id,
        url_root=request.url_root[:-1],
    )


@app.route("/join/<string:game_id>", methods=["POST", "GET"], strict_slashes=False)
def join_game(game_id):
    game = Game.query.filter_by(game_id=game_id).limit(1).first()
    if game is None:
        abort(404, description=f"Game {game_id} not found")

    if game_id in session.get("active_games", []):
        return redirect(url_for("game_page", game_id=game_id))

    form = GameJoinForm()
    if form.validate_on_submit():
        flash("User {} joined game {}".format(form.username.data, game.game_id))
        game.hat_picks.extend(
            [
                HatPick(name=name.data, submitter=form.username.data)
                for name in form.names
            ]
        )
        db.session.commit()

        session_games = session.get("active_games", [])
        session_games.append(game_id)
        session["active_games"] = session_games
        session.modified = True
        session.permanent = True

        return redirect(url_for("game_page", game_id=game_id))

    for n in range(len(form.names), game.n_picks):
        form.names.append_entry()

    return render_template(
        "game_join_form.html",
        title=f"Join {game.game_id}",
        game_id=game.game_id,
        url_root=request.url_root[:-1],
        form=form,
    )


@app.route("/game/<string:game_id>/hat-picks", methods=["GET"], strict_slashes=False)
def get_game_hat_picks(game_id):
    hat_picks = HatPick.query.join(Game).filter(Game.game_id == game_id).all()

    return jsonify([hat_pick.as_dict() for hat_pick in hat_picks])


@app.route(
    "/game/<string:game_id>/hat-picks/draw", methods=["POST"], strict_slashes=False
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
    "/game/<string:game_id>/hat-pick/<int:name_id>",
    methods=["PUT"],
    strict_slashes=False,
)
def update_name(game_id, name_id):
    hat_pick = HatPick.query.get(name_id)

    if hat_pick is None:
        abort(404, description=f"Hat pick {name_id} not found in game {game_id}")

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

    hat_pick.name = request.json.get("name", hat_pick.name)
    hat_pick.picked = request.json.get("picked", hat_pick.picked)
    hat_pick.timestamp = datetime.utcnow()

    if hat_pick.submitter != request.json.get("submitter", hat_pick.submitter):
        db.session.rollback()
        abort(403, "submitter field is immutable")
    if hat_pick.id != request.json.get("id", hat_pick.id):
        db.session.rollback()
        abort(403, "id field is immutable")
    if hat_pick.game_id != request.json.get("game_id", hat_pick.game_id):
        db.session.rollback()
        abort(403, "game_id field is immutable")

    # Write-back the chosen one
    db.session.commit()

    return jsonify({"hat_pick": hat_pick.as_dict()})


@app.route("/clean", methods=["POST"], strict_slashes=False)
def db_clean():
    app.logger.info("Cleanup")
    removed = Game.delete_expired()
    outcome = "Removed {} games".format(removed)
    app.logger.info(outcome)
    return outcome
