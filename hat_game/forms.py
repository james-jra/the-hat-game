from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList
from wtforms.validators import DataRequired, Length, Regexp


class GameJoinForm(FlaskForm):
    username = StringField(
        "Your Name",
        validators=[Length(0, 64), Regexp(r"[A-Za-z0-9 \-]"), DataRequired()],
    )
    names = FieldList(
        StringField(
            validators=[
                Length(0, 256),
                Regexp(r"[A-Za-z0-9 \,\.\-\(\)]"),
                DataRequired(),
            ],
            min_entries=4,
            max_entries=4,
        )
    )
    submit = SubmitField("Join")
