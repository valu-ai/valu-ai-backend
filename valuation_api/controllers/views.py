from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from valuation_api.models.entities import DistrictEnum
from valuation_api.dtos.serializers import (
    ValuationRequestDTO,
    PropertyValuationResponseDTO
)
from valuation_api.services.ml_service import MLValuationService
from valuation_api.repositories.property_repo import PropertyValuationRepository


class PropertyDistrictsListView(APIView):
    """
    Endpoint para obtener la lista oficial de distritos soportados por el modelo ML.
    """
    @extend_schema(
        summary="Listar distritos soportados",
        description="Devuelve el catálogo de distritos válidos para poblar menús desplegables o selectores en el frontend.",
        responses={200: OpenApiResponse(description="Lista de nombres de distritos válidos")},
        tags=["Valuations"]
    )
    def get(self, request):
        districts = [choice[0] for choice in DistrictEnum.choices]
        return Response({"districts": districts}, status=status.HTTP_200_OK)


class PropertyValuationEstimateView(APIView):
    """
    Endpoint para realizar la estimación de precio comercial de un inmueble.
    """
    @extend_schema(
        summary="Estimar precio de inmueble",
        description="Recibe las características obligatorias del inmueble, ejecuta la inferencia con el modelo ML y devuelve la estimación persistida en USD.",
        request=ValuationRequestDTO,
        responses={
            201: PropertyValuationResponseDTO,
            400: OpenApiResponse(description="Datos de entrada inválidos"),
            503: OpenApiResponse(description="Modelo ML no disponible")
        },
        tags=["Valuations"]
    )
    def post(self, request):
        serializer = ValuationRequestDTO(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "error": {
                        "code": "ValidationError",
                        "message": "Los datos del inmueble proporcionados son inválidos.",
                        "details": serializer.errors
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        valuation = MLValuationService.predict_and_save(serializer.validated_data)
        response_serializer = PropertyValuationResponseDTO(valuation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PropertyValuationListView(APIView):
    """
    Endpoint para listar el historial de estimaciones realizadas.
    """
    @extend_schema(
        summary="Listar valoraciones",
        description="Devuelve el historial completo de valoraciones realizadas ordenadas descendentemente por fecha.",
        responses={200: PropertyValuationResponseDTO(many=True)},
        tags=["Valuations"]
    )
    def get(self, request):
        valuations = PropertyValuationRepository.list_all()
        serializer = PropertyValuationResponseDTO(valuations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyValuationDetailView(APIView):
    """
    Endpoint para obtener los detalles de una valoración por ID.
    """
    @extend_schema(
        summary="Obtener valoración por ID",
        description="Consulta el registro detallado de una estimación específica mediante su identificador único.",
        responses={
            200: PropertyValuationResponseDTO,
            404: OpenApiResponse(description="Valoración no encontrada")
        },
        tags=["Valuations"]
    )
    def get(self, request, pk):
        valuation = PropertyValuationRepository.get_by_id(pk)
        if not valuation:
            return Response(
                {
                    "error": {
                        "code": "NotFound",
                        "message": f"No se encontró ninguna valoración con el ID {pk}.",
                        "details": None
                    }
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PropertyValuationResponseDTO(valuation)
        return Response(serializer.data, status=status.HTTP_200_OK)