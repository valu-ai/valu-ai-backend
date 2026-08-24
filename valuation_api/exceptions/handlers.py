from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Manejador global de excepciones para DRF.
    Estructura las respuestas de error en un formato JSON consistente.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            "error": {
                "code": exc.__class__.__name__,
                "message": "Se produjo un error al procesar la solicitud.",
                "details": response.data
            }
        }
        response.data = custom_response_data
    else:
        # Errores no capturados por DRF (ej. FileNotFoundError si falta el .joblib)
        if isinstance(exc, FileNotFoundError):
            return Response(
                {
                    "error": {
                        "code": "FileNotFoundError",
                        "message": str(exc),
                        "details": "El modelo de ML no se encuentra disponible en el servidor."
                    }
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Error genérico de servidor
        return Response(
            {
                "error": {
                    "code": "InternalServerError",
                    "message": "Ocurrió un error interno en el servidor.",
                    "details": str(exc)
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response