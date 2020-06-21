from datetime import datetime
from datetime import timedelta

from app import db

class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    modified = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    deleted = db.Column(db.DateTime, nullable=True)


    @classmethod
    def create(cls, **kw):
        #assumed kw is a clean user details
        try:
            obj = cls(**kw)
            db.session.add(obj)
            db.session.commit()

            return True
        except:
            db.session.rollback()
            return False

    @classmethod
    def get_all(cls):
        q = cls.query.all()

        if q is not None:
            return q

        return None

    
class Travel(BaseMixin, db.Model):
    __tablename__ = 'travels'

    description = db.Column(db.String(256), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    mode = db.Column(db.String(256), nullable=True)
    ticket_cost = db.Column(db.Float, default=0, nullable=True)
    home_airport_cab_cost = db.Column(db.Float, default=0, nullable=True)
    dest_airport_cab_cost = db.Column(db.Float, default=0, nullable=True)
    hotel_cost = db.Column(db.Float, default=0, nullable=True)
    local_conveyance = db.Column(db.Float, default=0, nullable=True)
    
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    @classmethod
    def create_with_return(cls, **kw):
        #assumed kw is a clean user details
        try:
            obj = cls(**kw)
            db.session.add(obj)
            db.session.commit()

            return obj
        except:
            db.session.rollback()
            return None 

    
    @classmethod
    def find_by_id(cls, id):
        q = cls.query.filter(cls.id==id).all()

        if q is not None:
            return q

        return None


    @classmethod
    def find_by_owner(cls, owner):
        q = cls.query.filter(cls.owner==owner).all()

        if q is not None:
            return q

        return None



class TravelImage(BaseMixin, db.Model):
    __tablename__ = 'travel_images'

    name = db.Column(db.String(256), nullable=False)
    
    travel = db.Column(db.Integer, db.ForeignKey('travels.id'), nullable=True)


class TravelApproval(BaseMixin, db.Model):
    __tablename__ = 'travel_approvals'

    travel = db.Column(db.Integer, db.ForeignKey('travels.id'), nullable=True)
    sender = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approver = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    #0 - draft
    #1 - submitted
    #2 - approved
    #3 - rejected
    #4 - request for information
    status = db.Column(db.Integer, default=0, nullable=False)

    
    @classmethod
    def find_by_approver(cls, approver):
        q = cls.query.filter(cls.approver==approver).all()

        if q is not None:
            return q

        return None
    
    
    @classmethod
    def find_by_status(cls, status):
        q = cls.query.filter(cls.status==status).all()

        if q is not None:
            return q

        return None
