import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException
import httpx

from backend.config import DAPTA_TIMEOUT_SECONDS
from backend.modelos.lead import EstadoLead
from backend.rutas import leads as rutas_leads
from backend.servicios.rag_agente import (
    DaptaAgentError,
    calificar_con_agente_dapta,
)


AGENT_ID = "a2f51962-1754-4ff4-a5d3-0082625607cc"


class CalificacionDaptaTests(unittest.TestCase):
    @patch("backend.servicios.rag_agente.httpx.post")
    def test_envia_categoria_y_respeta_veredicto_no_calificado(self, post):
        post.return_value = Mock(
            json=Mock(return_value={
                "agent_id": AGENT_ID,
                "output": "ESTADO: NO_CALIFICADO. SCORE: 0%. No cumple los criterios.",
            })
        )

        estado, score, feedback = calificar_con_agente_dapta(
            nombre_negocio="Taller Rapifix",
            sector="Mecánica Automotriz",
            canal="email",
            senal_dolor="Pocas solicitudes de servicio",
            opcion_elegida="A",
            lead_id="lead-123",
        )

        payload = post.call_args.kwargs["json"]
        self.assertEqual(
            payload["variables"]["perfil_cliente"],
            "Mecánica Automotriz",
        )
        self.assertEqual(
            payload["variables"]["datos_lead"]["perfil_cliente"],
            {"categoria": "Mecánica Automotriz"},
        )
        self.assertTrue(
            payload["message"].startswith("Califica este lead utilizando")
        )
        indice_calificar = payload["message"].index("Califica este lead")
        indice_perfil = payload["message"].index("El perfil del cliente")
        self.assertGreater(indice_perfil, indice_calificar)
        self.assertIn(
            "El perfil del cliente es la categoría del lead a calificar: "
            "Mecánica Automotriz.",
            payload["message"][indice_calificar:],
        )
        self.assertIn('"categoria": "Mecánica Automotriz"', payload["message"])
        self.assertIn(
            '"perfil_cliente": {"categoria": "Mecánica Automotriz"}',
            payload["message"],
        )
        self.assertIn(
            "El perfil del cliente es la categoría del lead a calificar",
            payload["message"],
        )
        self.assertIn(
            "El perfil del cliente es la categoría del lead a calificar: "
            "Mecánica Automotriz",
            payload["message"],
        )
        self.assertIn(
            "No hagas preguntas ni solicites información adicional.",
            payload["message"],
        )
        self.assertNotIn("ingreso", payload["message"].lower())
        self.assertNotIn("esfuerzo", payload["message"].lower())
        self.assertIn("SCORE: N%", payload["message"])
        self.assertIn('"respuesta_microsondeo": "A"', payload["message"])
        self.assertIn('"actividad_en_redes": "No informada"', payload["message"])
        self.assertTrue(payload["external_id"].startswith("lead-lead-123-"))
        self.assertEqual(post.call_args.kwargs["timeout"], DAPTA_TIMEOUT_SECONDS)
        self.assertEqual(estado, EstadoLead.NO_CALIFICADO.value)
        self.assertEqual(score, 0.0)
        self.assertIn("NO_CALIFICADO", feedback)

    @patch("backend.servicios.rag_agente.httpx.post")
    def test_recalificaciones_generan_una_solicitud_nueva_para_dapta(self, post):
        post.return_value = Mock(
            json=Mock(return_value={
                "agent_id": AGENT_ID,
                "output": "ESTADO: CALIFICADO. SCORE: 87%.",
            })
        )

        for _ in range(2):
            calificar_con_agente_dapta(
                nombre_negocio="Clínica Sonrisas",
                sector="Salud",
                lead_id="lead-123",
            )

        ids_externos = [
            llamada.kwargs["json"]["external_id"]
            for llamada in post.call_args_list
        ]
        self.assertEqual(len(ids_externos), 2)
        self.assertNotEqual(ids_externos[0], ids_externos[1])

    @patch("backend.servicios.rag_agente.httpx.post")
    def test_score_se_usa_solo_si_lo_devuelve_dapta(self, post):
        post.return_value = Mock(
            json=Mock(return_value={
                "agent_id": AGENT_ID,
                "output": "ESTADO: CALIFICADO. SCORE: 87%.",
            })
        )

        estado, score, _ = calificar_con_agente_dapta(
            nombre_negocio="Clínica Sonrisas",
            sector="Salud",
        )

        self.assertEqual(estado, EstadoLead.CALIFICADO.value)
        self.assertEqual(score, 0.87)

    def test_parsea_formatos_de_score_como_porcentaje(self):
        from backend.servicios.rag_agente import _extraer_score_dapta

        ejemplos = {
            "SCORE: 87%": 0.87,
            "Calificado - 87%": 0.87,
            "En revisión: 50%": 0.5,
            "No calificado (0%)": 0.0,
            "Puntaje de calidad: 87 de 100": 0.87,
            "Puntuación es 0,87": 0.87,
            "Porcentaje: 100 por ciento": 1.0,
            "Calificación: 0%": 0.0,
        }
        for respuesta, esperado in ejemplos.items():
            with self.subTest(respuesta=respuesta):
                self.assertEqual(_extraer_score_dapta(respuesta), esperado)

    @patch("backend.servicios.rag_agente.httpx.post")
    def test_usa_estado_y_porcentaje_en_respuesta_literal_del_agente(self, post):
        from backend.servicios.rag_agente import DaptaAgentError

        casos = [
            ("Calificado - 87%", EstadoLead.CALIFICADO.value, 0.87),
            ("En revisión - 50%", EstadoLead.EN_REVISION.value, 0.5),
            ("En revisión - 73%", EstadoLead.EN_REVISION.value, 0.73),
            ("En revisión - 74%", EstadoLead.CALIFICADO.value, 0.74),
            ("En revisión - 90%", EstadoLead.CALIFICADO.value, 0.9),
            ("No calificado - 12%", EstadoLead.NO_CALIFICADO.value, 0.12),
            ("No calificado - 87%", EstadoLead.NO_CALIFICADO.value, 0.87),
        ]
        for salida, estado_esperado, score_esperado in casos:
            with self.subTest(salida=salida):
                post.return_value = Mock(
                    json=Mock(return_value={
                        "agent_id": AGENT_ID,
                        "output": salida,
                    })
                )

                estado, score, feedback = calificar_con_agente_dapta(
                    nombre_negocio="Empresa Demo",
                    sector="Comercio",
                )

                self.assertEqual(estado, estado_esperado)
                self.assertEqual(score, score_esperado)
                self.assertEqual(feedback, salida)

    @patch("backend.servicios.rag_agente.httpx.post")
    def test_no_acepta_salida_con_estado_pero_sin_porcentaje(self, post):
        post.return_value = Mock(
            json=Mock(return_value={
                "agent_id": AGENT_ID,
                "output": "Calificado",
            })
        )

        with self.assertRaises(DaptaAgentError):
            calificar_con_agente_dapta(
                nombre_negocio="Empresa Demo",
                sector="Comercio",
            )

    def test_score_ausente_o_fuera_de_rango_no_es_aceptado(self):
        from backend.servicios.rag_agente import _extraer_score_dapta

        self.assertIsNone(_extraer_score_dapta("ESTADO: CALIFICADO"))
        self.assertIsNone(_extraer_score_dapta("SCORE: 140%"))

    def test_score_se_extrae_de_campos_estructurados_de_dapta(self):
        from backend.servicios.rag_agente import _extraer_score_dapta

        self.assertEqual(
            _extraer_score_dapta("Calificado", {"score_porcentaje": 87}),
            0.87,
        )
        self.assertEqual(
            _extraer_score_dapta("En revisión", {"score": "52%"}),
            0.52,
        )
        self.assertEqual(
            _extraer_score_dapta("No calificado", {"score": 0.12}),
            0.12,
        )

    def test_omite_numero_fuera_de_rango_y_toma_porcentaje_valido(self):
        from backend.servicios.rag_agente import _extraer_score_dapta

        self.assertEqual(
            _extraer_score_dapta("Calificación: 500. El resultado es 87%."),
            0.87,
        )

    @patch("backend.servicios.rag_agente.httpx.post")
    def test_score_sin_estado_explicito_califica_desde_el_umbral(self, post):
        post.return_value = Mock(
            json=Mock(return_value={
                "agent_id": AGENT_ID,
                "output": "SCORE: 82%. El equipo comercial les dará seguimiento.",
            })
        )

        estado, score, _ = calificar_con_agente_dapta(
            nombre_negocio="Restaurante El Buen Sabor",
            sector="Restaurante",
        )

        self.assertEqual(estado, EstadoLead.CALIFICADO.value)
        self.assertEqual(score, 0.82)

    @patch("backend.servicios.rag_agente.httpx.post")
    def test_prioriza_estado_explicito_sobre_la_justificacion(self, post):
        post.return_value = Mock(
            json=Mock(return_value={
                "agent_id": AGENT_ID,
                "output": "ESTADO: EN_REVISION. SCORE: 50%. Falta confirmar ingresos.",
            })
        )

        estado, _, _ = calificar_con_agente_dapta(
            nombre_negocio="Restaurante El Buen Sabor",
            sector="Restaurante",
        )

        self.assertEqual(estado, EstadoLead.EN_REVISION.value)

    @patch("backend.servicios.rag_agente.httpx.post")
    def test_usa_veredicto_de_cierre_emitido_por_el_agente(self, post):
        post.return_value = Mock(
            json=Mock(return_value={
                "agent_id": AGENT_ID,
                "output": "SCORE: 92%. El equipo comercial les dará seguimiento.",
                "tool_calls": [{
                    "name": "close_conversation",
                    "args": {"reason": "calificación completada; informar derivación comercial"},
                }],
            })
        )

        estado, _, _ = calificar_con_agente_dapta(
            nombre_negocio="Clínica Sonrisas",
            sector="Salud",
        )

        self.assertEqual(estado, EstadoLead.CALIFICADO.value)

    @patch("backend.servicios.rag_agente.httpx.post")
    def test_error_de_conexion_no_genera_calificacion_simulada(self, post):
        post.side_effect = httpx.ConnectError("conexión rechazada")

        with self.assertRaises(DaptaAgentError):
            calificar_con_agente_dapta(
                nombre_negocio="Clínica Sonrisas",
                sector="Salud",
            )

    @patch("backend.servicios.rag_agente.httpx.post")
    def test_timeout_de_dapta_indica_que_no_se_guardo(self, post):
        post.side_effect = httpx.ReadTimeout("lectura agotó el tiempo")

        with self.assertRaisesRegex(
            DaptaAgentError,
            rf"Dapta no respondió dentro de {DAPTA_TIMEOUT_SECONDS:g} segundos.*no se guardó",
        ):
            calificar_con_agente_dapta(
                nombre_negocio="Clínica Sonrisas",
                sector="Salud",
            )

    @patch("backend.rutas.leads.actualizar_estado_lead")
    @patch("backend.rutas.leads.obtener_lead_por_id")
    @patch("backend.rutas.leads.calificar_con_agente_dapta")
    def test_estado_persistido_es_el_veredicto_del_agente(
        self, calificar_agente, obtener_lead, actualizar_estado
    ):
        obtener_lead.return_value = {
            "id": "lead-123",
            "nombre_negocio": "Taller Rapifix",
            "sector": "Mecánica Automotriz",
            "canal": "email",
            "senal_dolor": "Pocas solicitudes",
            "opcion_respondida": "A",
            "propuesta_generada": None,
        }
        calificar_agente.return_value = (
            EstadoLead.NO_CALIFICADO.value,
            0.87,
            "ESTADO: NO_CALIFICADO",
        )

        respuesta = rutas_leads.calificar("lead-123")

        actualizar_estado.assert_called_once_with(
            "lead-123",
            EstadoLead.NO_CALIFICADO.value,
            {
                "calificado_dapta": 0,
                "score_calidad_dapta": 0.87,
                "feedback_dapta": "ESTADO: NO_CALIFICADO",
            },
        )
        self.assertEqual(respuesta["nuevo_estado"], EstadoLead.NO_CALIFICADO.value)
        self.assertEqual(respuesta["score_calidad_porcentaje"], 87.0)
        self.assertEqual(respuesta["categoria"], "Mecánica Automotriz")

    @patch("backend.rutas.leads.obtener_lead_por_id")
    @patch("backend.rutas.leads.calificar_con_agente_dapta")
    def test_error_de_dapta_no_actualiza_el_estado(self, calificar_agente, obtener_lead):
        obtener_lead.return_value = {
            "id": "lead-123",
            "nombre_negocio": "Taller Rapifix",
            "sector": "Mecánica Automotriz",
            "canal": "email",
            "senal_dolor": "Pocas solicitudes",
            "opcion_respondida": "A",
            "propuesta_generada": None,
        }
        calificar_agente.side_effect = DaptaAgentError("servicio no disponible")

        with patch("backend.rutas.leads.actualizar_estado_lead") as actualizar_estado:
            with self.assertRaises(HTTPException) as contexto:
                rutas_leads.calificar("lead-123")

        self.assertEqual(contexto.exception.status_code, 502)
        actualizar_estado.assert_not_called()


if __name__ == "__main__":
    unittest.main()
