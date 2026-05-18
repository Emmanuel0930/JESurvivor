"""
Patrón Adapter — Inversión de Dependencias para APIs de Terceros.
Requerimiento Entregable 2: Consumo de API de terceros mediante Adapter Pattern.

API consumida: Open-Meteo (https://open-meteo.com/)
- Gratuita, sin necesidad de API Key
- Proporciona datos de clima en tiempo real por coordenadas
- Relevancia de dominio: JESurvivor usa el clima para asesorar sobre kits de supervivencia

Arquitectura del patrón:
  IClimaAdapter (Puerto / Interfaz abstracta)
       ↑ implementa
  OpenMeteoAdapter (Adaptador concreto)
       ↑ usa
  ClimaService (Lógica de aplicación — no depende del adaptador concreto)
"""

import abc
import logging
import requests
from typing import Optional

logger = logging.getLogger("jesurvivor.adapters")


# ═══════════════════════════════════════════════════════
# PUERTO: Interfaz abstracta (Dependency Inversion)
# La capa de aplicación depende de ESTA abstracción,
# nunca del adaptador concreto directamente.
# ═══════════════════════════════════════════════════════

class IClimaAdapter(abc.ABC):
    """
    Puerto de salida: define el contrato para proveedores de clima.
    Si en el futuro cambiamos de Open-Meteo a OpenWeatherMap u otro,
    solo creamos un nuevo adaptador concreto sin tocar el resto del sistema.
    """

    @abc.abstractmethod
    def obtener_clima_actual(self, latitud: float, longitud: float) -> dict:
        """
        Retorna información climática para las coordenadas dadas.
        
        Returns:
            dict con claves: temperatura_c, viento_kmh, precipitacion_mm,
                             descripcion, condicion, fuente
        """
        ...

    @abc.abstractmethod
    def obtener_nombre_proveedor(self) -> str:
        """Retorna el nombre del proveedor (para logging y respuestas)."""
        ...


# ═══════════════════════════════════════════════════════
# ADAPTADOR CONCRETO: Open-Meteo
# Traduce la API de Open-Meteo al contrato IClimaAdapter
# ═══════════════════════════════════════════════════════

class OpenMeteoAdapter(IClimaAdapter):
    """
    Adaptador concreto para la API gratuita Open-Meteo.
    Traduce el formato de respuesta de Open-Meteo al contrato IClimaAdapter.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    TIMEOUT_SEGUNDOS = 8

    # Códigos WMO de clima → descripciones en español
    _CODIGOS_WMO = {
        0: ("Cielo despejado", "sunny"),
        1: ("Principalmente despejado", "sunny"),
        2: ("Parcialmente nublado", "cloudy"),
        3: ("Cubierto / Nublado", "cloudy"),
        45: ("Niebla", "foggy"),
        48: ("Niebla con escarcha", "foggy"),
        51: ("Llovizna ligera", "rainy"),
        53: ("Llovizna moderada", "rainy"),
        55: ("Llovizna densa", "rainy"),
        61: ("Lluvia ligera", "rainy"),
        63: ("Lluvia moderada", "rainy"),
        65: ("Lluvia intensa", "rainy"),
        71: ("Nieve ligera", "snowy"),
        73: ("Nieve moderada", "snowy"),
        75: ("Nieve intensa", "snowy"),
        80: ("Chubascos ligeros", "rainy"),
        81: ("Chubascos moderados", "rainy"),
        82: ("Chubascos intensos", "rainy"),
        85: ("Nieve en chubascos", "snowy"),
        95: ("Tormenta eléctrica", "stormy"),
        99: ("Tormenta con granizo intenso", "stormy"),
    }

    def obtener_nombre_proveedor(self) -> str:
        return "Open-Meteo"

    def obtener_clima_actual(self, latitud: float, longitud: float) -> dict:
        """
        Consulta la API de Open-Meteo y retorna datos normalizados.
        """
        try:
            response = requests.get(
                self.BASE_URL,
                params={
                    "latitude": latitud,
                    "longitude": longitud,
                    "current": [
                        "temperature_2m",
                        "wind_speed_10m",
                        "precipitation",
                        "weathercode",
                        "relative_humidity_2m",
                        "apparent_temperature",
                    ],
                    "timezone": "auto",
                    "wind_speed_unit": "kmh",
                },
                timeout=self.TIMEOUT_SEGUNDOS,
            )
            response.raise_for_status()
            data = response.json()
            current = data.get("current", {})
            codigo = current.get("weathercode", 0)
            descripcion, condicion = self._CODIGOS_WMO.get(codigo, (f"Código {codigo}", "unknown"))

            return {
                "temperatura_c": current.get("temperature_2m"),
                "sensacion_termica_c": current.get("apparent_temperature"),
                "humedad_pct": current.get("relative_humidity_2m"),
                "viento_kmh": current.get("wind_speed_10m"),
                "precipitacion_mm": current.get("precipitation"),
                "codigo_wmo": codigo,
                "descripcion": descripcion,
                "condicion": condicion,
                "fuente": self.obtener_nombre_proveedor(),
                "error": None,
            }

        except requests.Timeout:
            logger.warning("[OpenMeteoAdapter] Timeout al consultar clima lat=%s lon=%s", latitud, longitud)
            return self._respuesta_error("Timeout al conectar con Open-Meteo")
        except requests.HTTPError as e:
            logger.error("[OpenMeteoAdapter] HTTP Error: %s", e)
            return self._respuesta_error(f"Error HTTP: {e}")
        except Exception as e:
            logger.error("[OpenMeteoAdapter] Error inesperado: %s", e)
            return self._respuesta_error(str(e))

    def _respuesta_error(self, mensaje: str) -> dict:
        return {
            "temperatura_c": None,
            "sensacion_termica_c": None,
            "humedad_pct": None,
            "viento_kmh": None,
            "precipitacion_mm": None,
            "codigo_wmo": None,
            "descripcion": "No disponible",
            "condicion": "unknown",
            "fuente": self.obtener_nombre_proveedor(),
            "error": mensaje,
        }


# ═══════════════════════════════════════════════════════
# SERVICIO DE CLIMA — usa el adaptador por inyección
# ═══════════════════════════════════════════════════════

# Coordenadas representativas por entorno de supervivencia (Colombia)
COORDENADAS_POR_ENTORNO = {
    "montana": {"lat": 4.570868, "lon": -74.297333, "lugar": "Cordillera Central, Colombia"},
    "selva":   {"lat": 1.2136,   "lon": -77.2811,   "lugar": "Amazonía colombiana"},
    "urbano":  {"lat": 6.2442,   "lon": -75.5812,   "lugar": "Medellín, Colombia"},
    "desierto": {"lat": 11.5444, "lon": -72.9072,   "lugar": "La Guajira, Colombia"},
    "nieve":   {"lat": 4.8087,   "lon": -75.6906,   "lugar": "Nevado del Ruiz, Colombia"},
}


class ClimaService:
    """
    Servicio de aplicación para consultas de clima.
    Depende de IClimaAdapter, no de la implementación concreta.
    Permite cambiar de proveedor sin modificar este servicio (DIP).
    """

    def __init__(self, adapter: Optional[IClimaAdapter] = None):
        # Por defecto usa OpenMeteoAdapter (inyectable en tests)
        self._adapter = adapter or OpenMeteoAdapter()

    def obtener_clima_para_entorno(self, entorno: str) -> dict:
        """
        Retorna clima y recomendaciones de supervivencia para un entorno.
        """
        entorno = entorno.lower().strip()
        coords = COORDENADAS_POR_ENTORNO.get(entorno, COORDENADAS_POR_ENTORNO["urbano"])

        clima = self._adapter.obtener_clima_actual(coords["lat"], coords["lon"])

        return {
            "entorno": entorno,
            "lugar_referencia": coords["lugar"],
            "coordenadas": {"lat": coords["lat"], "lon": coords["lon"]},
            "clima": clima,
            "recomendacion_kit": self._recomendar_kit(clima, entorno),
            "alerta_supervivencia": self._generar_alerta(clima),
        }

    def _recomendar_kit(self, clima: dict, entorno: str) -> str:
        """Recomienda un tipo de kit según el clima y el entorno."""
        if clima.get("error"):
            return "Kit universal de emergencia (datos de clima no disponibles)"

        temp = clima.get("temperatura_c") or 20
        condicion = clima.get("condicion", "unknown")

        if condicion == "snowy" or (temp is not None and temp < 5):
            return "Kit de montaña con equipo térmico, crampones y baliza GPS"
        elif condicion == "stormy":
            return "Kit de tormenta: refugio rápido, poncho, radio meteorológico"
        elif condicion == "rainy":
            return "Kit tropical: ropa impermeable, purificador de agua, machete"
        elif entorno == "desierto":
            return "Kit desértico: 4L agua/día, protector solar, espejo de señales"
        elif entorno == "selva":
            return "Kit de selva: anti-mosquitos, hamaca, navaja multiusos, botiquín"
        else:
            return "Kit estándar de supervivencia urbana o terreno moderado"

    def _generar_alerta(self, clima: dict) -> Optional[str]:
        """Genera alerta si las condiciones son peligrosas."""
        if clima.get("error"):
            return None

        condicion = clima.get("condicion", "")
        temp = clima.get("temperatura_c")
        viento = clima.get("viento_kmh")

        alertas = []
        if condicion == "stormy":
            alertas.append("⚠️ TORMENTA ACTIVA — busca refugio inmediato")
        if temp is not None and temp < 0:
            alertas.append("🥶 RIESGO DE CONGELAMIENTO — hipotermia posible")
        if temp is not None and temp > 38:
            alertas.append("🔥 RIESGO DE GOLPE DE CALOR — hidratación crítica")
        if viento is not None and viento > 60:
            alertas.append("💨 VIENTOS EXTREMOS — evitar zonas expuestas")

        return " | ".join(alertas) if alertas else None
