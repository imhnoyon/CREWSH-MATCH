from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if 'detail' in response.data:
            response.data['message'] = response.data.pop('detail')

    if response is not None and isinstance(exc, ValidationError):
        flat_errors = {}
        for key, value in response.data.items():
            if isinstance(value, list) and len(value) == 1:
                flat_errors[key] = value[0]  # Flatten single-item lists
            else:
                flat_errors[key] = value
        response.data = flat_errors

    return response
