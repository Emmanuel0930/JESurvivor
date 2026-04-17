import requests
import json
import time

BASE_URL = "http://localhost"  # Asumiendo que corre en el puerto 80 vía Nginx

def test_health():
    print("\n[1] Probando Health Check (Flask via Nginx)...")
    try:
        r = requests.get(f"{BASE_URL}/api/v2/reservas/health")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_list_kits():
    print("\n[2] Listando Kits desde Microservicio (Flask)...")
    try:
        r = requests.get(f"{BASE_URL}/api/v2/reservas/kits")
        print(f"Status: {r.status_code}")
        kits = r.json()
        print(f"Total kits encontrados: {len(kits)}")
        if kits:
            print(f"Primer kit: {kits[0]['nombre']} - Stock: {kits[0]['stock']}")
    except Exception as e:
        print(f"Error: {e}")

def test_create_reserva_fail():
    print("\n[3] Probando validación de error (400 - Campos faltantes)...")
    try:
        r = requests.post(f"{BASE_URL}/api/v2/reservas/crear", json={"usuario_id": 1})
        print(f"Status: {r.status_code} (Esperado: 400)")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_legacy_django():
    print("\n[4] Probando acceso al Monolito Legacy (Django)...")
    try:
        # Intentamos acceder a la documentación de Swagger en Django
        r = requests.get(f"{BASE_URL}/api/docs/")
        print(f"Status: {r.status_code} (Esperado: 200)")
        if r.status_code == 200:
            print("El monolito Django sigue respondiendo correctamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=== INICIANDO PRUEBAS DEL PATRÓN ESTRANGULADOR ===")
    test_health()
    test_list_kits()
    test_create_reserva_fail()
    test_legacy_django()
    print("\n=== PRUEBAS FINALIZADAS ===")
