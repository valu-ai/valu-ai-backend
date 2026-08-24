from django.test import TestCase
from valuation_api.repositories.property_repo import PropertyValuationRepository
from valuation_api.models.entities import PropertyValuationEntity


class PropertyValuationRepositoryTestCase(TestCase):
    """
    Pruebas unitarias para la capa de acceso a datos (PropertyValuationRepository).
    """

    def test_create_valuation_persists_in_db(self):
        """Verifica que el repositorio guarde un registro en la base de datos."""
        valuation = PropertyValuationRepository.create(
            area_m2=90.0,
            bedrooms=3,
            bathrooms=2,
            parking_spaces=1,
            age_years=5,
            district="Miraflores",
            estimated_price_usd=150000.0
        )

        self.assertIsNotNone(valuation.id)
        self.assertEqual(valuation.district, "Miraflores")
        self.assertEqual(valuation.estimated_price_usd, 150000.0)
        self.assertEqual(PropertyValuationEntity.objects.count(), 1)

    def test_get_by_id_returns_correct_entity_or_none(self):
        """Verifica la búsqueda por ID para registros existentes y no existentes."""
        created = PropertyValuationRepository.create(
            area_m2=80.0,
            bedrooms=2,
            bathrooms=2,
            parking_spaces=1,
            age_years=2,
            district="San Isidro",
            estimated_price_usd=180000.0
        )

        found = PropertyValuationRepository.get_by_id(created.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, created.id)

        not_found = PropertyValuationRepository.get_by_id(99999)
        self.assertIsNone(not_found)

    def test_list_all_returns_descending_order(self):
        """Verifica que list_all devuelva todos los registros ordenados por fecha."""
        PropertyValuationRepository.create(
            area_m2=50.0, bedrooms=1, bathrooms=1, parking_spaces=0,
            age_years=10, district="Surquillo", estimated_price_usd=90000.0
        )
        PropertyValuationRepository.create(
            area_m2=120.0, bedrooms=3, bathrooms=3, parking_spaces=2,
            age_years=1, district="San Borja", estimated_price_usd=220000.0
        )

        valuations = PropertyValuationRepository.list_all()
        self.assertEqual(valuations.count(), 2)
        self.assertEqual(valuations[0].district, "San Borja")