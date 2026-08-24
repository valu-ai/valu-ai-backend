from django.test import TestCase
from valuation_api.dtos.serializers import ValuationRequestDTO


class ValuationDTOsTestCase(TestCase):
    """
    Pruebas de validación para el DTO de entrada ValuationRequestDTO.
    """

    def test_valid_payload_passes_validation(self):
        """Verifica que un payload correcto sea válido."""
        payload = {
            "area_m2": 85.5,
            "bedrooms": 3,
            "bathrooms": 2,
            "parking_spaces": 1,
            "age_years": 5,
            "district": "Miraflores"
        }
        serializer = ValuationRequestDTO(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_invalid_district_fails_validation(self):
        """Verifica que un distrito que no pertenezca al Enum falle."""
        payload = {
            "area_m2": 85.5,
            "bedrooms": 3,
            "bathrooms": 2,
            "parking_spaces": 1,
            "age_years": 5,
            "district": "DistritoFicticio"
        }
        serializer = ValuationRequestDTO(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("district", serializer.errors)

    def test_negative_area_fails_validation(self):
        """Verifica que un área negativa o menor a 1.0 m² sea rechazada."""
        payload = {
            "area_m2": -10.0,
            "bedrooms": 3,
            "bathrooms": 2,
            "district": "Miraflores"
        }
        serializer = ValuationRequestDTO(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("area_m2", serializer.errors)