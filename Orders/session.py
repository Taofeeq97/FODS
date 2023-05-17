def _session_id(request):
    session_id = request.session.session_key
    if not session_id:
        session_id = request.session.create()
    return session_id

