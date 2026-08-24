from typing import Optional
from django.db.models import QuerySet
from valuation_api.models.entities import PropertyValuationEntity


class PropertyValuationRepository:
    """
    Capa de acceso a datos para la entidad PropertyValuationEntity.
    """

    @staticmethod
    def create(
        area_m2: float,
        bedrooms: int,
        bathrooms: int,
        parking_spaces: int,
        age_years: int,
        district: str,
        estimated_price_usd: Optional[float] = None
    ) -> PropertyValuationEntity:
        return PropertyValuationEntity.objects.create(
            area_m2=area_m2,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            parking_spaces=parking_spaces,
            age_years=age_years,
            district=district,
            estimated_price_usd=estimated_price_usd
        )

    @staticmethod
    def get_by_id(valuation_id: int) -> Optional[PropertyValuationEntity]:
        try:
            return PropertyValuationEntity.objects.get(pk=valuation_id)
        except PropertyValuationEntity.DoesNotExist:
            return None

    @staticmethod
    def list_all() -> QuerySet[PropertyValuationEntity]:
        return PropertyValuationEntity.objects.all().order_by('-created_at')