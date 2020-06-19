from datetime import datetime
from datetime import timedelta

from app import db

class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    modified = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    deleted = db.Column(db.DateTime, nullable=True)


class Travel(BaseMixin, db.Model):
    __tablename__ = 'travels'

    description = db.Column(db.String(256), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.DateTime, nullable=False)
    ticket_cost = db.Column(db.Float, default=0, nullable=False)
    home_airport_cab_cost = db.Column(db.Float, default=0, nullable=False)
    dest_airport_cab_cost = db.Column(db.Float, default=0, nullable=False)
    hotel_cost = db.Column(db.Float, default=0, nullable=False)
