from rest_framework import serializers
from valuation_api.models.entities import PropertyValuationEntity
from valuation_api.models.enums import DistrictEnum


class ValuationRequestDTO(serializers.Serializer):
    """
    DTO / Serializador de Entrada (Request)
    Valida estrictamente los 6 inputs requeridos por el modelo de ML.
    """
    area_m2 = serializers.FloatField(
        min_value=1.0,
        required=True,
        error_messages={
            'invalid': 'El área debe ser un número válido.',
            'min_value': 'El área (m²) debe ser mayor o igual a 1.0.'
        },
        help_text="Área total en metros cuadrados"
    )
    bedrooms = serializers.IntegerField(
        min_value=0,
        required=True,
        error_messages={
            'invalid': 'El número de dormitorios debe ser un entero.',
            'min_value': 'El número de dormitorios no puede ser negativo.'
        },
        help_text="Número de dormitorios"
    )
    bathrooms = serializers.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            'invalid': 'El número de baños debe ser un entero.',
            'min_value': 'El número de baños debe ser al menos 1.'
        },
        help_text="Número de baños"
    )
    parking_spaces = serializers.IntegerField(
        min_value=0,
        default=0,
        required=False,
        error_messages={
            'invalid': 'El número de estacionamientos debe ser un entero.',
            'min_value': 'El número de estacionamientos no puede ser negativo.'
        },
        help_text="Número de estacionamientos / cocheras"
    )
    age_years = serializers.IntegerField(
        min_value=0,
        default=0,
        required=False,
        error_messages={
            'invalid': 'La antigüedad debe ser un número entero de años.',
            'min_value': 'La antigüedad no puede ser negativa.'
        },
        help_text="Antigüedad del inmueble en años"
    )
    district = serializers.ChoiceField(
        choices=DistrictEnum.choices,
        required=True,
        error_messages={
            'invalid_choice': 'El distrito proporcionado no está dentro de la lista permitida por el modelo ML.'
        },
        help_text="Distrito exacto donde se ubica el inmueble"
    )

    def validate_district(self, value):
        """
        Validación personalizada para asegurar que el distrito retorne
        el valor exacto esperado por el codificador/modelo ML.
        """
        if value not in DistrictEnum.values:
            raise serializers.ValidationError("Distrito no soportado por el modelo.")
        return value


class PropertyValuationResponseDTO(serializers.ModelSerializer):
    """
    DTO / Serializador de Salida (Response)
    Formatea la entidad de valoración persistida con el precio estimado en USD.
    """
    class Meta:
        model = PropertyValuationEntity
        fields = [
            'id',
            'area_m2',
            'bedrooms',
            'bathrooms',
            'parking_spaces',
            'age_years',
            'district',
            'estimated_price_usd',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'estimated_price_usd',
            'created_at',
            'updated_at',
        ]