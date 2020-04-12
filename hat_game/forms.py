from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class GameJoinForm(FlaskForm):
    username = StringField(
        "Your Name",
        validators=[Length(0, 64), Regexp(r"[A-Za-z0-9 \-]"), DataRequired()],
    )
    names_0 = StringField(
        "",
        validators=[Length(0, 256), Regexp(r"[A-Za-z0-9 \,\.\-\(\)]"), DataRequired()],
    )
    names_1 = StringField(
        "",
        validators=[Length(0, 256), Regexp(r"[A-Za-z0-9 \,\.\-\(\)]"), DataRequired()],
    )
    names_2 = StringField(
        "",
        validators=[Length(0, 256), Regexp(r"[A-Za-z0-9 \,\.\-\(\)]"), DataRequired()],
    )
    names_3 = StringField(
        "",
        validators=[Length(0, 256), Regexp(r"[A-Za-z0-9 \,\.\-\(\)]"), DataRequired()],
    )
    submit = SubmitField("Join")
