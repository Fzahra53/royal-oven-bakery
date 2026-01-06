class AdminSessionTimeoutMiddleware:
    """
    For /admin/ only:
    - session expires after 10 minutes of inactivity
    - only for authenticated staff users
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            user = getattr(request, "user", None)
            if user and user.is_authenticated and user.is_staff:
                # 600 seconds = 10 minutes
                request.session.set_expiry(600)

        return self.get_response(request)
