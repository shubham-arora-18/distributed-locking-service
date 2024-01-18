from fastapi import status


class CustomException(Exception):
    def __init__(self, detail: str, status_code: int):
        super().__init__(detail, status_code)
        self.detail = detail
        self.status_code = status_code


class InvalidInputException(CustomException):
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class InternalServerException(CustomException):
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_500_INTERNAL_SERVER_ERROR)


class DuplicateDataException(CustomException):
    def __init__(self, detail: str, status_code: int):
        super().__init__(detail, status_code)


class MissingDataException(CustomException):
    def __init__(self, detail: str):
        super().__init__(f"Missing data: {detail}", status.HTTP_404_NOT_FOUND)


class AuthException(CustomException):
    def __init__(self, detail: str, status_code: int):
        super().__init__(detail, status_code)
