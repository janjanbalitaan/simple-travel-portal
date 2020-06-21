from flask import jsonify, request
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import or_

from app import app
from app import db
from app.models.travel import Travel
from app.models.travel import TravelApproval
from app.models.travel import TravelImage
from app.models.user import User
from app.models.user import UserToken 
from app.utilities.response import ResponseUtilities as ru
from app.utilities.validation import ValidationUtilities as vu

status_values = {'draft': 0, 'submitted': 1, 'approved': 2, 'rejected': 3, 'request': 4}
status_values_reverse = {0: 'draft', 1: 'submitted', 2: 'approved', 3: 'rejected', 4: 'request'}
role_values_reverse = {1: 'admin' , 2: 'finance_manager' , 3: 'manager', 4: 'employee'}

for_values = {'draft': 0, 'submitted': 1}

@app.route('/api/employee/travels', methods=['POST'])
def create_travel_record():
    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    if 'description' not in request.get_json():
        return ru.http_bad_gateway(message="Description is required in the request")

    if 'start_date' not in request.get_json():
        return ru.http_bad_gateway(message="Start date is required in the request")
    else:
        if request.get_json().get('start_date') is None:
            pass
        else:
            if not vu.is_valid_datetime_string(request.get_json().get('start_date')):
                return ru.http_bad_gateway(message="Start date must be in format YYYY-MM-DD")

    if 'end_date' not in request.get_json():
        return ru.http_bad_gateway(message="End date is required in the request")
    else:
        if request.get_json().get('end_date') is None:
            pass
        else:
            if not vu.is_valid_datetime_string(request.get_json().get('end_date')):
                return ru.http_bad_gateway(message="End date must be in format YYYY-MM-DD")

            if request.get_json().get('start_date') > request.get_json().get('end_date'):
                return ru.http_bad_gateway(message="End date must be greater than or equal to start date")


    if 'mode' not in request.get_json():
        return ru.http_bad_gateway(message="Mode is required in the request")

    if 'ticket_cost' not in request.get_json():
        return ru.http_bad_gateway(message="Ticket cost is required in the request")
    else:
        if request.get_json().get('ticket_cost') is None:
            pass
        else:
            if not (type(request.get_json().get('ticket_cost')) == int or type(request.get_json().get('ticket_cost')) == float):
                return ru.http_bad_gateway(message="Ticket cost must be numeric")

    if 'home_airport_cost' not in request.get_json():
        return ru.http_bad_gateway(message="Home airport cost is required in the request")
    else:
        if request.get_json().get('home_airport_cost') is None:
            pass
        else:
            if not (type(request.get_json().get('home_airport_cost')) == int or type(request.get_json().get('home_airport_cost')) == float):
                return ru.http_bad_gateway(message="Home airport cost must be numeric")

    if 'destination_airport_cost' not in request.get_json():
        return ru.http_bad_gateway(message="Destination airport cost is required in the request")
    else:
        if request.get_json().get('destination_airport_cost') is None:
            pass
        else:
            if not (type(request.get_json().get('destination_airport_cost')) == int or type(request.get_json().get('destination_airport_cost')) == float):
                return ru.http_bad_gateway(message="Destination aiport cost must be numeric")

    if 'hotel_cost' not in request.get_json():
        return ru.http_bad_gateway(message="Hotel cost is required in the request")
    else:
        if request.get_json().get('hotel_cost') is None:
            pass
        else:
            if not (type(request.get_json().get('hotel_cost')) == int or type(request.get_json().get('hotel_cost')) == float):
                return ru.http_bad_gateway(message="Hotel cost must be numeric")

    if 'local_conveyance' not in request.get_json():
        return ru.http_bad_gateway(message="Local conveyance is required in the request")
    else:
        if request.get_json().get('local_conveyance') is None:
            pass
        else:
            if not (type(request.get_json().get('local_conveyance')) == int or type(request.get_json().get('local_conveyance')) == float):
                return ru.http_bad_gateway(message="Local conveyance cost must be numeric")
    
    manager_id = None
    if 'approver' not in request.get_json():
        return ru.http_bad_gateway(message="Approver is required in the request")
    else:
        if request.get_json().get('approver') is None:
            pass
        else:
            manager = User.find_by_uid(request.get_json().get('approver'))
            if manager is None:
                return ru.http_bad_gateway(message="Invalid manager")
            
            if not manager.is_manager:
                return ru.http_bad_gateway(message="Invalid manager")

            manager_id = manager.id

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()

    is_submitted = 1
    if for_values.get(request.args.get('for')) is not None:
        is_submitted = for_values.get(request.args.get('for'))

    if is_submitted == 1:
        if manager_id is None:
            return ru.http_conflict(message="Manager must be required when submitting for approval")

    if user.is_employee:
        travel = Travel.create_with_return(
                description=request.get_json().get('description'),
                start_date=request.get_json().get('start_date'),
                end_date=request.get_json().get('end_date'),
                mode=request.get_json().get('mode'),
                ticket_cost=request.get_json().get('ticket_cost'),
                home_airport_cab_cost=request.get_json().get('home_airport_cost'),
                dest_airport_cab_cost=request.get_json().get('destination_airport_cost'),
                hotel_cost=request.get_json().get('hotel_cost'),
                local_conveyance=request.get_json().get('local_conveyance'),
                owner=user.id,
                )

        if travel is None:
            return ru.http_conflict(message="Failed to save your travel details")
        else:
            ta = TravelApproval.create(travel=travel.id, sender=user.id, approver=manager_id, status=is_submitted)

            if not ta:
                return ru.http_conflict(message="Failed to save your travel approval details")

        return ru.http_created(message="successfully created")
    else:
        return ru.http_forbidden(message='Role is not allowed to create a travel record')


@app.route('/api/employee/travels/<int:id>', methods=['PUT'])
def update_travel_record(id):
    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    if 'description' not in request.get_json():
        return ru.http_bad_gateway(message="Description is required in the request")

    if 'start_date' not in request.get_json():
        return ru.http_bad_gateway(message="Start date is required in the request")
    else:
        if request.get_json().get('start_date') is None:
            pass
        else:
            if not vu.is_valid_datetime_string(request.get_json().get('start_date')):
                return ru.http_bad_gateway(message="Start date must be in format YYYY-MM-DD")

    if 'end_date' not in request.get_json():
        return ru.http_bad_gateway(message="End date is required in the request")
    else:
        if request.get_json().get('end_date') is None:
            pass
        else:
            if not vu.is_valid_datetime_string(request.get_json().get('end_date')):
                return ru.http_bad_gateway(message="End date must be in format YYYY-MM-DD")

            if request.get_json().get('start_date') > request.get_json().get('end_date'):
                return ru.http_bad_gateway(message="End date must be greater than or equal to start date")


    if 'mode' not in request.get_json():
        return ru.http_bad_gateway(message="Mode is required in the request")

    if 'ticket_cost' not in request.get_json():
        return ru.http_bad_gateway(message="Ticket cost is required in the request")
    else:
        if request.get_json().get('ticket_cost') is None:
            pass
        else:
            if not (type(request.get_json().get('ticket_cost')) == int or type(request.get_json().get('ticket_cost')) == float):
                return ru.http_bad_gateway(message="Ticket cost must be numeric")

    if 'home_airport_cost' not in request.get_json():
        return ru.http_bad_gateway(message="Home airport cost is required in the request")
    else:
        if request.get_json().get('home_airport_cost') is None:
            pass
        else:
            if not (type(request.get_json().get('home_airport_cost')) == int or type(request.get_json().get('home_airport_cost')) == float):
                return ru.http_bad_gateway(message="Home airport cost must be numeric")

    if 'destination_airport_cost' not in request.get_json():
        return ru.http_bad_gateway(message="Destination airport cost is required in the request")
    else:
        if request.get_json().get('destination_airport_cost') is None:
            pass
        else:
            if not (type(request.get_json().get('destination_airport_cost')) == int or type(request.get_json().get('destination_airport_cost')) == float):
                return ru.http_bad_gateway(message="Destination aiport cost must be numeric")

    if 'hotel_cost' not in request.get_json():
        return ru.http_bad_gateway(message="Hotel cost is required in the request")
    else:
        if request.get_json().get('hotel_cost') is None:
            pass
        else:
            if not (type(request.get_json().get('hotel_cost')) == int or type(request.get_json().get('hotel_cost')) == float):
                return ru.http_bad_gateway(message="Hotel cost must be numeric")

    if 'local_conveyance' not in request.get_json():
        return ru.http_bad_gateway(message="Local conveyance is required in the request")
    else:
        if request.get_json().get('local_conveyance') is None:
            pass
        else:
            if not (type(request.get_json().get('local_conveyance')) == int or type(request.get_json().get('local_conveyance')) == float):
                return ru.http_bad_gateway(message="Local conveyance cost must be numeric")
    
    manager_id = None
    if 'approver' not in request.get_json():
        return ru.http_bad_gateway(message="Approver is required in the request")
    else:
        if request.get_json().get('approver') is None:
            pass
        else:
            manager = User.find_by_uid(request.get_json().get('approver'))
            if manager is None:
                return ru.http_bad_gateway(message="Invalid manager")
            
            if not manager.is_manager:
                return ru.http_bad_gateway(message="Invalid manager")

            manager_id = manager.id

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()

    is_submitted = 1
    if for_values.get(request.args.get('for')) is not None:
        is_submitted = for_values.get(request.args.get('for'))

    if is_submitted == 1:
        if manager_id is None:
            return ru.http_conflict(message="Manager must be required when submitting for approval")

    if user.is_employee:
        sub = db.session.query(
                TravelApproval.id.label('ta_id'),
                TravelApproval.created.label('ta_created'),
                TravelApproval.deleted.label('ta_deleted'),
                TravelApproval.modified.label('ta_modified'),
                TravelApproval.travel.label('ta_travel'),
                TravelApproval.sender.label('ta_sender'),
                TravelApproval.approver.label('ta_approver'),
                TravelApproval.status.label('ta_status'),
                ).filter(TravelApproval.travel==id).order_by(desc(TravelApproval.id)).limit(1).subquery()

        query = db.session.query(Travel, TravelApproval).join(sub, sub.c.ta_travel == Travel.id, isouter=False).join(User, sub.c.ta_approver == User.id, isouter=True).filter(Travel.owner==user.id, Travel.id==id).first()

        print(query)

        if query is None:
            return ru.http_bad_gateway(message="The data is not available for update")


        if query[1] is not None:
            if query[1].status != 0 or query[1].sender != user.id:
                return ru.http_conflict(message="The data is not available for update")


        if query is None:
            return ru.http_conflict(message="Failed to update your travel details")

        query[0].description=request.get_json().get('description'),
        query[0].start_date=request.get_json().get('start_date'),
        query[0].end_date=request.get_json().get('end_date'),
        query[0].mode=request.get_json().get('mode'),
        query[0].ticket_cost=request.get_json().get('ticket_cost'),
        query[0].home_airport_cab_cost=request.get_json().get('home_airport_cost'),
        query[0].dest_airport_cab_cost=request.get_json().get('destination_airport_cost'),
        query[0].hotel_cost=request.get_json().get('hotel_cost'),
        query[0].local_conveyance=request.get_json().get('local_conveyance'),

        if query[1] is None:
            ta = TravelApproval.create(travel=query[0].id, sender=user.id, approver=manager_id, status=is_submitted)
        else:
            query[1].travel=query[0].id
            query[1].sender=user.id
            query[1].approver=manager_id
            query[1].status=is_submitted

        db.session.commit()


        return ru.http_created(message="successfully updated")
    else:
        return ru.http_forbidden(message='Role is not allowed to update a travel record')


@app.route('/api/employee/travels', methods=['GET'])
def get_travel_record():
    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()


    if user.is_employee:
        travels = Travel.find_by_owner(user.id)
        
        meta = []

        if travels is not None:
            for travel in travels:
                query = db.session.query(TravelApproval, User).join(User, TravelApproval.approver == User.id, isouter=True).filter(travel.id==TravelApproval.travel)
            
                if status_values.get(request.args.get('status')) is not None:
                    sub = db.session.query(TravelApproval.status).filter(TravelApproval.travel==travel.id).order_by(desc(TravelApproval.id)).limit(1)

                    query = query.filter(TravelApproval.status==sub, TravelApproval.status==status_values.get(request.args.get('status')))

                query = query.order_by(desc(TravelApproval.id)).limit(1)
                

                for row in query.all():
                    print(row)
                    a = row[0]
                    u = row[1]

                    #t_ : for travel object
                    #ta_ : for travel approval object
                    #u_ : for user object

                    if a is not  None:
                        meta.append({
                            't_id': travel.id,
                            't_created': travel.created,
                            't_modified': travel.modified,
                            't_description': travel.description,
                            't_start_date': travel.start_date,
                            't_end_date': travel.end_date,
                            't_mode': travel.mode,
                            't_ticket_cost': travel.ticket_cost,
                            't_home_airport_cost': travel.home_airport_cab_cost,
                            't_destination_airport_cost': travel.dest_airport_cab_cost,
                            't_hotel_cost': travel.hotel_cost,
                            't_local_conveyance': travel.local_conveyance,
                            'ta_status': status_values_reverse.get(a.status),
                            'u_id': u.uid,
                            'u_email': u.email,
                            'u_first_name': u.first_name,
                            'u_last_name': u.last_name,
                            'u_role': role_values_reverse.get(u.role)
                            })
                    else:
                        meta.append({
                            't_id': travel.id,
                            't_created': travel.created,
                            't_modified': travel.modified,
                            't_description': None,
                            't_start_date': travel.start_date,
                            't_end_date': travel.end_date,
                            't_mode': travel.mode,
                            't_ticket_cost': travel.ticket_cost,
                            't_home_airport_cost': travel.home_airport_cab_cost,
                            't_destination_airport_cost': travel.dest_airport_cab_cost,
                            't_hotel_cost': travel.hotel_cost,
                            't_local_conveyance': travel.local_conveyance,
                            'ta_status': None,
                            'u_id': None,
                            'u_email': None,
                            'u_first_name': None,
                            'u_last_name': None,
                            'u_role': None,
                            })


        return ru.http_success(message="successfully fetched", meta=meta)
    else:
        return ru.http_forbidden(message='Role is not allowed to access this resource')


@app.route('/api/manager/travels', methods=['GET'])
def get_travel_manager_record():
    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()


    if user.is_manager:
        travels = db.session.query(Travel).join(TravelApproval, TravelApproval.travel == Travel.id).filter(or_(TravelApproval.approver==user.id, TravelApproval.sender==user.id)).all()

        meta = []

        if travels is not None:
            for travel in travels:
                query = db.session.query(TravelApproval, User).join(User, TravelApproval.approver == User.id, isouter=True).filter(travel.id==TravelApproval.travel)
            
                if status_values.get(request.args.get('status')) is not None:
                    sub = db.session.query(TravelApproval.status).filter(TravelApproval.travel==travel.id).order_by(desc(TravelApproval.id)).limit(1)

                    query = query.filter(TravelApproval.status==sub, TravelApproval.status==status_values.get(request.args.get('status')))

                query = query.order_by(desc(TravelApproval.id)).limit(1)
                

                for row in query.all():
                    print(row)
                    a = row[0]
                    u = row[1]

                    #t_ : for travel object
                    #ta_ : for travel approval object
                    #u_ : for user object

                    if a is not  None:
                        meta.append({
                            't_id': travel.id,
                            't_created': travel.created,
                            't_modified': travel.modified,
                            't_description': travel.description,
                            't_start_date': travel.start_date,
                            't_end_date': travel.end_date,
                            't_mode': travel.mode,
                            't_ticket_cost': travel.ticket_cost,
                            't_home_airport_cost': travel.home_airport_cab_cost,
                            't_destination_airport_cost': travel.dest_airport_cab_cost,
                            't_hotel_cost': travel.hotel_cost,
                            't_local_conveyance': travel.local_conveyance,
                            'ta_status': status_values_reverse.get(a.status),
                            'u_id': u.uid,
                            'u_email': u.email,
                            'u_first_name': u.first_name,
                            'u_last_name': u.last_name,
                            'u_role': role_values_reverse.get(u.role)
                            })
                    else:
                        meta.append({
                            't_id': travel.id,
                            't_created': travel.created,
                            't_modified': travel.modified,
                            't_description': None,
                            't_start_date': travel.start_date,
                            't_end_date': travel.end_date,
                            't_mode': travel.mode,
                            't_ticket_cost': travel.ticket_cost,
                            't_home_airport_cost': travel.home_airport_cab_cost,
                            't_destination_airport_cost': travel.dest_airport_cab_cost,
                            't_hotel_cost': travel.hotel_cost,
                            't_local_conveyance': travel.local_conveyance,
                            'ta_status': None,
                            'u_id': None,
                            'u_email': None,
                            'u_first_name': None,
                            'u_last_name': None,
                            'u_role': None,
                            })


        return ru.http_success(message="successfully fetched", meta=meta)
    else:
        return ru.http_forbidden(message='Role is not allowed to access this resource')


@app.route('/api/manager/travels/<int:id>/approval', methods=['PUT'])
def approve_record_by_manager(id):
    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    if request.get_json().get('status') is None:
        return ru.http_bad_gateway(message="Status is required")

    if status_values.get(request.get_json().get('status')) is None or status_values.get(request.get_json().get('status')) not in (2, 3):
        return ru.http_bad_gateway(message="Status is invalid")

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()


    if user.is_manager:
        travel = db.session.query(Travel).join(TravelApproval, TravelApproval.travel == Travel.id).filter(TravelApproval.approver==user.id, TravelApproval.status==1, Travel.id==id).first()

        if travel is None:
            return ru.http_conflict(message="No travel available for update")

        ta = db.session.query(TravelApproval).filter(travel.id==TravelApproval.travel).order_by(desc(TravelApproval.id)).limit(1).first()

        if ta is None:
            return ru.http_conflict(message="No data available for update")

        #if not submitted
        if ta.status != 1:
            return ru.http_conflict(message="Data is not available for update")

        if ta.approver != user.id:
            return ru.http_conflict(message="Data is not available for update of the user")

        ta.status = status_values.get(request.get_json().get('status'))
        db.session.commit()
        
        return ru.http_success()
    else:
        return ru.http_forbidden(message='Role is not allowed to access this resource')


@app.route('/api/manager/travels/<int:id>/submission', methods=['POST'])
def submit_to_finance_manager_by_manager(id):
    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    finance_manager_id = None
    if 'approver' not in request.get_json():
        return ru.http_bad_gateway(message="Approver is required in the request")
    else:
        if request.get_json().get('approver') is None:
            pass
        else:
            finance_manager = User.find_by_uid(request.get_json().get('approver'))
            if finance_manager is None:
                return ru.http_bad_gateway(message="Invalid manager")
            
            if not finance_manager.is_finance_manager:
                return ru.http_bad_gateway(message="Invalid manager")

            finance_manager_id = finance_manager.id

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()


    if user.is_manager:
        travel = db.session.query(Travel).join(TravelApproval, TravelApproval.travel == Travel.id).filter(TravelApproval.approver==user.id, TravelApproval.status==2, Travel.id==id).first()

        if travel is None:
            return ru.http_conflict(message="No travel available for update")

        ta = db.session.query(TravelApproval).filter(travel.id==TravelApproval.travel).order_by(desc(TravelApproval.id)).limit(1).first()

        if ta is None:
            return ru.http_conflict(message="No data available for update")

        #if not submitted
        if ta.status != 2:
            return ru.http_conflict(message="Data is not available for update")

        if ta.approver != user.id:
            return ru.http_conflict(message="Data is not available for update of the user")

        TravelApproval.create(status=1, travel=travel.id, sender=user.id, approver=finance_manager_id)

        return ru.http_success()
    else:
        return ru.http_forbidden(message='Role is not allowed to access this resource')


@app.route('/api/finance/travels', methods=['GET'])
def get_travel_finance_record():
    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()


    if user.is_finance_manager:
        travels = db.session.query(Travel).join(TravelApproval, TravelApproval.travel == Travel.id).filter(or_(TravelApproval.approver==user.id, TravelApproval.sender==user.id)).all()

        meta = []

        if travels is not None:
            for travel in travels:
                query = db.session.query(TravelApproval, User).join(User, TravelApproval.approver == User.id, isouter=True).filter(travel.id==TravelApproval.travel)
            
                if status_values.get(request.args.get('status')) is not None:
                    sub = db.session.query(TravelApproval.status).filter(TravelApproval.travel==travel.id).order_by(desc(TravelApproval.id)).limit(1)

                    query = query.filter(TravelApproval.status==sub, TravelApproval.status==status_values.get(request.args.get('status')))

                query = query.order_by(desc(TravelApproval.id)).limit(1)
                

                for row in query.all():
                    a = row[0]
                    u = row[1]

                    #t_ : for travel object
                    #ta_ : for travel approval object
                    #u_ : for user object

                    if a is not  None:
                        meta.append({
                            't_id': travel.id,
                            't_created': travel.created,
                            't_modified': travel.modified,
                            't_description': travel.description,
                            't_start_date': travel.start_date,
                            't_end_date': travel.end_date,
                            't_mode': travel.mode,
                            't_ticket_cost': travel.ticket_cost,
                            't_home_airport_cost': travel.home_airport_cab_cost,
                            't_destination_airport_cost': travel.dest_airport_cab_cost,
                            't_hotel_cost': travel.hotel_cost,
                            't_local_conveyance': travel.local_conveyance,
                            'ta_status': status_values_reverse.get(a.status),
                            'u_id': u.uid,
                            'u_email': u.email,
                            'u_first_name': u.first_name,
                            'u_last_name': u.last_name,
                            'u_role': role_values_reverse.get(u.role)
                            })
                    else:
                        meta.append({
                            't_id': travel.id,
                            't_created': travel.created,
                            't_modified': travel.modified,
                            't_description': None,
                            't_start_date': travel.start_date,
                            't_end_date': travel.end_date,
                            't_mode': travel.mode,
                            't_ticket_cost': travel.ticket_cost,
                            't_home_airport_cost': travel.home_airport_cab_cost,
                            't_destination_airport_cost': travel.dest_airport_cab_cost,
                            't_hotel_cost': travel.hotel_cost,
                            't_local_conveyance': travel.local_conveyance,
                            'ta_status': None,
                            'u_id': None,
                            'u_email': None,
                            'u_first_name': None,
                            'u_last_name': None,
                            'u_role': None,
                            })


        return ru.http_success(message="successfully fetched", meta=meta)
    else:
        return ru.http_forbidden(message='Role is not allowed to access this resource')


@app.route('/api/finance/travels/<int:id>/approval', methods=['PUT'])
def approve_record_by_finance_manager(id):
    #TODO: separate to a validation class
    if request.get_json() is None:
        return ru.http_unsupported_media_type()

    if request.get_json().get('status') is None:
        return ru.http_bad_gateway(message="Status is required")

    if status_values.get(request.get_json().get('status')) is None or status_values.get(request.get_json().get('status')) not in (2, 3):
        return ru.http_bad_gateway(message="Status is invalid")

    auth = request.headers.get('authorization').split(' ')

    if not vu.is_valid_bearer(auth):
        return ru.http_unauthorized(message="Invalid Bearer Authentication")

    token = UserToken.is_valid_token(auth[1])

    if token is None:
        return ru.http_unauthorized(message="Invalid token")

    if token.is_blocked or token.is_expired:
        return ru.http_forbidden()

    user = User.find_by_id(token.user)

    if user is None:
        return ru.http_forbidden()


    if user.is_finance_manager:
        travel = db.session.query(Travel).join(TravelApproval, TravelApproval.travel == Travel.id).filter(TravelApproval.approver==user.id, TravelApproval.status==1, Travel.id==id).first()

        if travel is None:
            print(123)
            return ru.http_conflict(message="No travel available for update")

        ta = db.session.query(TravelApproval).filter(travel.id==TravelApproval.travel).order_by(desc(TravelApproval.id)).limit(1).first()

        if ta is None:
            return ru.http_conflict(message="No data available for update")

        #if not submitted
        if ta.status != 1:
            return ru.http_conflict(message="Data is not available for update")

        if ta.approver != user.id:
            return ru.http_conflict(message="Data is not available for update of the user")

        ta.status = status_values.get(request.get_json().get('status'))
        db.session.commit()
        
        return ru.http_success()
    else:
        return ru.http_forbidden(message='Role is not allowed to access this resource')


