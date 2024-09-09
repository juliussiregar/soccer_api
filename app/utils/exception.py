from fastapi import status


class CustomException(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status = status_code
        self.message = message


class UnprocessableException(CustomException):
    def __init__(self, message):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class NotFoundException(CustomException):
    def __init__(self, message):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class InternalErrorException(CustomException):
    def __init__(self, message):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnauthorizedException(CustomException):
    def __init__(self, message):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)
