def unauthenticated_user_session_id(request):
    session_id = request.session.get('unauthenticated_user_session_id')
    if not session_id:
        session_id = request.session.create()
        request.session['unauthenticated_user_session_id'] = session_id
    return session_id
