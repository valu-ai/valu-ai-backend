import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from django.conf import settings
from valuation_api.repositories.property_repo import PropertyValuationRepository
from valuation_api.models.entities import PropertyValuationEntity

# Rutas principales del sistema
RESOURCE_DIR = Path(settings.BASE_DIR) / 'valuation_api' / 'resources' / 'ml_models'
DATA_DIR = Path(settings.BASE_DIR) / 'valuation_api' / 'resources' / 'data'

# Factores de contingencia por defecto (BCRP)
FALLBACK_FACTOR_SOLES = 1.65
FALLBACK_FACTOR_USD = 0.45


class MLValuationService:
    """
    Servicio de Inferencia ML de Valu.ai.
    Replica fielmente la carga del bundle, transformación de características,
    corrección de sesgo y post-procesamiento financiero de precios actualizados.
    """
    _model = None
    _features = []
    _bias_log = 0.0
    _f_usd = FALLBACK_FACTOR_USD
    _f_soles = FALLBACK_FACTOR_SOLES
    _label_to_col = {}

    @classmethod
    def _compute_conversion_factors(cls):
        """
        Calcula los factores de conversión desde precio base 2009 a precios actuales
        utilizando venta_ready.csv si existe.
        """
        possible_csv_paths = [
            DATA_DIR / "venta_ready.csv",
            RESOURCE_DIR / "venta_ready.csv",
            Path(settings.BASE_DIR) / "DATA" / "venta_ready.csv"
        ]

        venta_path = next((p for p in possible_csv_paths if p.exists()), None)
        if not venta_path:
            return FALLBACK_FACTOR_SOLES, FALLBACK_FACTOR_USD

        try:
            df = pd.read_csv(venta_path)
            max_year = int(df['anio'].max())
            df_recent = df[df['anio'] == max_year].copy()

            factor_soles = (df_recent['precio_soles_corrientes'] / df_recent['precio_target']).mean()
            factor_usd = (df_recent['precio_usd'] / df_recent['precio_target']).mean()

            return float(factor_soles), float(factor_usd)
        except Exception:
            return FALLBACK_FACTOR_SOLES, FALLBACK_FACTOR_USD

    @classmethod
    def _load_engine(cls):
        """
        Carga el bundle del modelo, extrae características, bias y mapeo de distritos.
        """
        if cls._model is not None:
            return

        possible_model_paths = [
            RESOURCE_DIR / "valu_model.joblib",
            RESOURCE_DIR / "model.joblib",
            Path(settings.BASE_DIR) / "artifacts" / "model.joblib"
        ]

        model_path = next((p for p in possible_model_paths if p.exists()), None)

        if not model_path:
            raise FileNotFoundError(
                f"No se encontró el archivo del modelo en {RESOURCE_DIR}. "
                "Asegúrate de colocar 'model.joblib' o 'valu_model.joblib' en 'valuation_api/resources/ml_models/'."
            )

        bundle = joblib.load(model_path)

        # Extraer componentes del bundle según el diseño del trainer
        if isinstance(bundle, dict):
            cls._model = bundle.get("model", bundle)
            cls._features = bundle.get("features", [])
            cls._bias_log = float(bundle.get("bias_log", 0.0))
        else:
            cls._model = bundle
            cls._features = []
            cls._bias_log = 0.0

        # Mapeo de columnas de distritos (ejemplo: 'distrito_Miraflores' -> 'Miraflores')
        distrito_map = {
            c: c.replace("distrito_", "")
            for c in cls._features
            if c.startswith("distrito_")
        }
        cls._label_to_col = {label: col for col, label in distrito_map.items()}

        # Cargar factores de conversión de moneda
        cls._f_soles, cls._f_usd = cls._compute_conversion_factors()

    @classmethod
    def predict_and_save(cls, validated_data: dict) -> PropertyValuationEntity:
        """
        Ejecuta el flujo completo de valoración de inmueble:
        1. Construcción del vector de características exactas.
        2. Inferencia con corrección de sesgo logarítmico.
        3. Conversión a USD con factor BCRP/venta_ready.csv.
        4. Persistencia en la base de datos local.
        """
        cls._load_engine()

        sup = float(validated_data['area_m2'])
        hab = int(validated_data['bedrooms'])
        ban = int(validated_data['bathrooms'])
        gar = int(validated_data.get('parking_spaces', 0))
        ant = int(validated_data.get('age_years', 0))
        dist = str(validated_data['district'])

        # 1. Creación del vector de características (X)
        if cls._features:
            row = {f: 0.0 for f in cls._features}
            row["log_superficie"] = np.log1p(sup)
            row["banos"] = ban
            row["garajes"] = gar
            row["antiguedad"] = ant
            row["habitaciones"] = hab

            # Marcar el distrito correspondiente en 1.0 (One-Hot)
            col_dist = cls._label_to_col.get(dist)
            if not col_dist:
                col_dist = f"distrito_{dist}"

            if col_dist in row:
                row[col_dist] = 1.0

            X = pd.DataFrame([row], columns=cls._features)
        else:
            # Fallback en caso de que el joblib no contenga la lista 'features'
            X = pd.DataFrame([{
                'area_m2': sup,
                'bedrooms': hab,
                'bathrooms': ban,
                'parking_spaces': gar,
                'age_years': ant,
                'district': dist,
            }])

        # 2. Inferencia y corrección de sesgo (Bias Correction)
        y_log = float(cls._model.predict(X)[0])
        y_log += cls._bias_log

        # 3. Post-procesamiento (Escalado de Soles 2009 a USD Actuales)
        p_constante_2009 = np.expm1(y_log)
        p_usd = p_constante_2009 * cls._f_usd

        estimated_price = round(float(p_usd), 2)

        # 4. Guardar en SQLite vía Repositorio
        return PropertyValuationRepository.create(
            area_m2=validated_data['area_m2'],
            bedrooms=validated_data['bedrooms'],
            bathrooms=validated_data['bathrooms'],
            parking_spaces=validated_data.get('parking_spaces', 0),
            age_years=validated_data.get('age_years', 0),
            district=validated_data['district'],
            estimated_price_usd=estimated_price
        )