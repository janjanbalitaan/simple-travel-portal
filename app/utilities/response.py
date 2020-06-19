from flask import jsonify


class ResponseUtilities:
    
    
    def http_success(status='success', message='Successful', meta=None):
        if meta is None:
            return jsonify({'status': status, 'code': 200, 'message': message}), 200
        else:
            return jsonify({'status': status, 'code': 200, 'message': message, 'meta': meta}), 200
    
    
    def http_created(status='success', message='Created'):
        return jsonify({'status': status, 'code': 201, 'message': message}), 201
    
    
    def http_bad_gateway(status='error', message='Bad gateway'):
        return jsonify({'status': status, 'code': 400, 'message': message}), 400
    
    
    def http_unauthorized(status='error', message='Unauthorized access'):
        return jsonify({'status': status, 'code': 401, 'message': message}), 401
    
    
    def http_forbidden(status='error', message='Forbidden access'):
        return jsonify({'status': status, 'code': 403, 'message': message}), 403
    
    
    def http_method_not_allowed(status='error', message='Method not allowed'):
        return jsonify({'status': status, 'code': 405, 'message': message}), 405
    
    
    def http_conflict(status='error', message='Conflict'):
        return jsonify({'status': status, 'code': 409, 'message': message}), 409
    
    
    def http_unsupported_media_type(status='error', message='Unsupported Media Type'):
        return jsonify({'status': status, 'code': 415, 'message': message}), 405
