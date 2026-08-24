from django.db import models
from .enums import DistrictEnum


class PropertyValuationEntity(models.Model):
    # Inputs obligatorios para el modelo de ML
    area_m2 = models.FloatField(
        help_text="Área total en metros cuadrados"
    )
    bedrooms = models.IntegerField(
        help_text="Número de dormitorios"
    )
    bathrooms = models.IntegerField(
        help_text="Número de baños"
    )
    parking_spaces = models.IntegerField(
        default=0,
        help_text="Número de estacionamientos / cocheras"
    )
    age_years = models.IntegerField(
        default=0,
        help_text="Antigüedad del inmueble en años"
    )
    district = models.CharField(
        max_length=50,
        choices=DistrictEnum.choices,
        help_text="Distrito exacto de ubicación"
    )

    # Output del modelo ML (calculado durante la valoración)
    estimated_price_usd = models.FloatField(
        null=True,
        blank=True,
        help_text="Precio estimado comercial en USD generado por el modelo ML"
    )

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'property_valuations'
        verbose_name = 'Property Valuation'
        verbose_name_plural = 'Property Valuations'

    def __str__(self):
        return f"Valuation {self.id} - {self.district} ({self.area_m2} m²) - USD {self.estimated_price_usd}"