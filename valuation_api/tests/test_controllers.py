from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from valuation_api.repositories.property_repo import PropertyValuationRepository


class ValuationControllersTestCase(APITestCase):
    """
    Pruebas de integración HTTP para las vistas de la API.
    """

    def test_estimate_endpoint_creates_valuation(self):
        """Prueba una estimación exitosa vía POST /api/v1/valuations/estimate/"""
        url = reverse('valuation-estimate')
        payload = {
            "area_m2": 90.0,
            "bedrooms": 3,
            "bathrooms": 2,
            "parking_spaces": 1,
            "age_years": 5,
            "district": "Miraflores"
        }
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("estimated_price_usd", response.data)
        self.assertGreater(response.data["estimated_price_usd"], 0)
        self.assertEqual(response.data["district"], "Miraflores")

    def test_estimate_endpoint_returns_400_on_invalid_data(self):
        """Prueba que la API responda HTTP 400 Bad Request cuando el payload es incorrecto."""
        url = reverse('valuation-estimate')
        payload = {
            "area_m2": -5.0,
            "bedrooms": 3,
            "bathrooms": 2,
            "district": "Miraflores"
        }
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"]["code"], "ValidationError")

    def test_list_valuations_endpoint(self):
        """Prueba la consulta de lista vía GET /api/v1/valuations/"""
        PropertyValuationRepository.create(
            area_m2=75.0, bedrooms=2, bathrooms=1, parking_spaces=1,
            age_years=3, district="Lince", estimated_price_usd=110000.0
        )
        url = reverse('valuation-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_detail_valuation_endpoint_not_found(self):
        """Prueba que un ID inexistente devuelva HTTP 404 Not Found en formato JSON estandarizado."""
        url = reverse('valuation-detail', kwargs={'pk': 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"]["code"], "NotFound")