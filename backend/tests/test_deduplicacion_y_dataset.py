"""
tests/test_deduplicacion_y_dataset.py — Verificación de deduplicación y dataset de 50 empresas
"""

import unittest
import uuid
from backend.base_datos.conexion import (
    inicializar_base_datos,
    insertar_lead,
    buscar_lead_duplicado,
    obtener_nombres_leads_existentes,
)
from backend.servicios.scraper import (
    _PYMES_GOOGLE_MAPS,
    _PYMES_PORTALES_EMPLEO,
    _PYMES_AUDITORIA_WEB,
    detectar_leads,
)


class TestDeduplicacionYDataset(unittest.TestCase):
    def setUp(self):
        inicializar_base_datos()

    def test_catalogo_contiene_50_empresas(self):
        total = len(_PYMES_GOOGLE_MAPS) + len(_PYMES_PORTALES_EMPLEO) + len(_PYMES_AUDITORIA_WEB)
        self.assertEqual(total, 50)
        self.assertEqual(len(_PYMES_GOOGLE_MAPS), 22)
        self.assertEqual(len(_PYMES_PORTALES_EMPLEO), 15)
        self.assertEqual(len(_PYMES_AUDITORIA_WEB), 13)

    def test_todas_las_pymes_tienen_campos_requeridos(self):
        todas = _PYMES_GOOGLE_MAPS + _PYMES_PORTALES_EMPLEO + _PYMES_AUDITORIA_WEB
        nombres = set()
        for p in todas:
            self.assertTrue(p.get("nombre_negocio"))
            self.assertTrue(p.get("sector"))
            self.assertTrue(p.get("ciudad"))
            self.assertTrue(p.get("telefono"))
            self.assertTrue(p.get("senal_dolor"))
            self.assertTrue(p.get("tipo_senal"))
            self.assertTrue(p.get("email"))
            nombres.add(p["nombre_negocio"].strip().lower())
        # No deben haber nombres repetidos entre las 50 semillas
        self.assertEqual(len(nombres), 50)

    def test_deduplicacion_por_nombre_y_telefono(self):
        id_1 = str(uuid.uuid4())
        token = uuid.uuid4().hex[:8]
        nombre_test = f"Empresa Test {token}"
        tel_test = f"+57 399 {uuid.uuid4().int % 10000000:07d}"
        email_test = f"test_{token}@ejemplo.co"

        lead_data = {
            "id": id_1,
            "nombre_negocio": nombre_test,
            "sector": "comercio",
            "ciudad": "Bogotá",
            "telefono": tel_test,
            "email": email_test,
            "sitio_web": "ejemplo.co",
            "senal_dolor": "Prueba de señal",
            "tipo_senal": "test_senal",
            "fuente_deteccion": "google_maps",
            "canal": "email",
            "estado": "detectado",
            "fecha_deteccion": "2026-10-18T10:00:00",
        }

        # Primera inserción exitosa
        res1 = insertar_lead(lead_data, permitir_duplicados=False)
        self.assertIsNotNone(res1)
        self.assertEqual(res1, id_1)

        # Intento de inserción con el mismo nombre -> debe rechazar
        lead_duplicado_nombre = dict(lead_data)
        lead_duplicado_nombre["id"] = str(uuid.uuid4())
        lead_duplicado_nombre["telefono"] = f"+57 399 {uuid.uuid4().int % 10000000:07d}"
        lead_duplicado_nombre["email"] = f"otro_{token}@ejemplo.co"
        res2 = insertar_lead(lead_duplicado_nombre, permitir_duplicados=False)
        self.assertIsNone(res2)

        # Intento de inserción con diferente nombre pero mismo teléfono -> debe rechazar
        lead_duplicado_tel = dict(lead_data)
        lead_duplicado_tel["id"] = str(uuid.uuid4())
        lead_duplicado_tel["nombre_negocio"] = f"Otra Empresa {token}"
        res3 = insertar_lead(lead_duplicado_tel, permitir_duplicados=False)
        self.assertIsNone(res3)

        # Intento de inserción con diferente nombre y teléfono pero mismo email -> debe rechazar
        lead_duplicado_email = dict(lead_data)
        lead_duplicado_email["id"] = str(uuid.uuid4())
        lead_duplicado_email["nombre_negocio"] = f"Tercera Empresa {token}"
        lead_duplicado_email["telefono"] = f"+57 399 {uuid.uuid4().int % 10000000:07d}"
        res4 = insertar_lead(lead_duplicado_email, permitir_duplicados=False)
        self.assertIsNone(res4)

    def test_obtener_nombres_leads_existentes(self):
        nombres = obtener_nombres_leads_existentes()
        self.assertIsInstance(nombres, set)


if __name__ == "__main__":
    unittest.main()
