from datetime import datetime, timedelta
from hat_game import db


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(256), index=True, unique=True)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    hat_picks = db.relationship("HatPick", backref="game", lazy=True)

    def __repr__(self):
        return "<Game {}>".format(self.game_id)

    @classmethod
    def delete_expired(cls):
        expiration_days = 1
        limit = datetime.utcnow() - timedelta(days=expiration_days)
        games_q = cls.query.filter(cls.created <= limit)
        for game in games_q.all():
            HatPick.query.filter(HatPick.game_id == game.id).delete()

        count = games_q.delete()
        db.session.commit()
        return count

    def as_dict(self):
        return {
            "id": self.id,
            "game_id": self.game_id,
            "created": self.created,
        }


class HatPick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    picked = db.Column(db.Boolean, default=False)
    submitter = db.Column(db.String(256))
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "<HatPick {} in game {}>".format(self.name, self.game_id)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "picked": self.picked,
            "submitter": self.submitter,
            "game_id": self.game_id,
            "timestamp": self.timestamp,
        }
