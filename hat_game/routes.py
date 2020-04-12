from flask import render_template, url_for, make_response
from hat_game import app, id_generator
from hat_game.forms import GameJoinForm


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Home")


@app.route("/game/<string:game_id>", methods=["POST", "GET"])
def game_page(game_id):
    form = GameJoinForm()
    # if form.validate_on_submit():
    #     # flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
    #     return redirect('/index')
    return render_template(
        "game_join_form.html", title="Join {game_id}", game_id=game_id, form=form
    )
    # return render_template(
    #     "game.html", title="Game {}".format(game_id), game_id=game_id
    # )


@app.route("/games", methods=["POST"])
def create_game():
    game_id = id_generator.get_id()
    # Check it doesn't conflict with existing game.
    game_url = url_for("game_page", game_id=game_id)
    resp = make_response("", 201)
    resp.headers["Location"] = game_url
    return resp
