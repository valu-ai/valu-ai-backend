from rest_framework import serializers
from valuation_api.models.entities import PropertyValuationEntity
from valuation_api.models.enums import DistrictEnum


class ValuationRequestDTO(serializers.Serializer):
    """
    DTO / Serializador de Entrada (Request)
    Valida estrictamente los 6 inputs requeridos por el modelo de ML,
    aplicando límites lógicos de mercado para evitar anomalías en predicciones.
    """
    area_m2 = serializers.FloatField(
        min_value=15.0,
        max_value=2000.0,
        required=True,
        error_messages={
            'invalid': 'El área debe ser un número válido.',
            'min_value': 'El área (m²) debe ser mayor o igual a 15.0 (miniestudio).',
            'max_value': 'El área (m²) excede el límite permitido (2000.0).'
        },
        help_text="Área total en metros cuadrados (15.0 a 2000.0)"
    )
    bedrooms = serializers.IntegerField(
        min_value=0,
        max_value=15,
        required=True,
        error_messages={
            'invalid': 'El número de dormitorios debe ser un entero.',
            'min_value': 'El número de dormitorios no puede ser negativo.',
            'max_value': 'El número de dormitorios no puede exceder 15.'
        },
        help_text="Número de dormitorios (0 a 15)"
    )
    bathrooms = serializers.IntegerField(
        min_value=1,
        max_value=10,
        required=True,
        error_messages={
            'invalid': 'El número de baños debe ser un entero.',
            'min_value': 'El número de baños debe ser al menos 1.',
            'max_value': 'El número de baños no puede exceder 10.'
        },
        help_text="Número de baños (1 a 10)"
    )
    parking_spaces = serializers.IntegerField(
        min_value=0,
        max_value=10,
        default=0,
        required=False,
        error_messages={
            'invalid': 'El número de estacionamientos debe ser un entero.',
            'min_value': 'El número de estacionamientos no puede ser negativo.',
            'max_value': 'El número de estacionamientos no puede exceder 10.'
        },
        help_text="Número de estacionamientos / cocheras (0 a 10)"
    )
    age_years = serializers.IntegerField(
        min_value=0,
        max_value=100,
        default=0,
        required=False,
        error_messages={
            'invalid': 'La antigüedad debe ser un número entero de años.',
            'min_value': 'La antigüedad no puede ser negativa.',
            'max_value': 'La antigüedad no puede exceder los 100 años.'
        },
        help_text="Antigüedad del inmueble en años (0 a 100)"
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