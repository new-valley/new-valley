class TooManyRequestsError(PermissionError):
    def __init__(self, message, *args):
        self.status_code = 429
        super().__init__(message)
