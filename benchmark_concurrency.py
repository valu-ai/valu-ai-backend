import time
import json
import random
import urllib.request
import urllib.error

API_URL = "http://127.0.0.1:8000/api/v1/valuations/estimate/"

# Distritos con la nomenclatura exacta aceptada por DistrictEnum
DISTRICTS = [
    "Miraflores", "San Isidro", "Santiago de Surco", "San Borja",
    "La Molina", "Barranco", "Jesús María", "Lince", "Magdalena del Mar",
    "Pueblo Libre", "San Miguel", "Surquillo"
]

def generate_random_property():
    return {
        "area_m2": round(random.uniform(50.0, 180.0), 1),
        "bedrooms": random.randint(1, 4),
        "bathrooms": random.randint(1, 3),
        "parking_spaces": random.randint(0, 2),
        "age_years": random.randint(0, 20),
        "district": random.choice(DISTRICTS)
    }

def send_single_request(req_id: int):
    payload = generate_random_property()
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            body = json.loads(response.read().decode('utf-8'))
            elapsed = time.perf_counter() - start
            return {
                "id": req_id,
                "status": status_code,
                "time": elapsed,
                "success": True,
                "district": payload["district"],
                "area_m2": payload["area_m2"],
                "price_usd": body.get("estimated_price_usd")
            }
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - start
        error_detail = e.read().decode('utf-8')
        return {"id": req_id, "status": e.code, "time": elapsed, "success": False, "error": error_detail}
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"id": req_id, "status": 0, "time": elapsed, "success": False, "error": str(e)}

def run_paced_test(total_requests=10, delay_seconds=2):
    print("=" * 70)
    print("🛰️  SIMULACIÓN CON DISTRITOS FORMATEADOS")
    print(f"Total de peticiones:    {total_requests}")
    print(f"Intervalo:              {delay_seconds} segundos")
    print("=" * 70)

    results = []

    for i in range(1, total_requests + 1):
        print(f"\n[Petición #{i:02d}/{total_requests:02d}] Procesando... ", end="", flush=True)
        res = send_single_request(i)
        results.append(res)

        if res["success"]:
            print(f"✅ OK (201 Created)")
            print(f"   ├─ Distrito:     {res['district']}")
            print(f"   ├─ Área:         {res['area_m2']} m²")
            print(f"   ├─ Precio Est.:  ${res['price_usd']:,.2f} USD")
            print(f"   └─ Tiempo resp.: {res['time']:.3f} s")
        else:
            print(f"❌ Error {res.get('status')}: {res.get('error')}")

        if i < total_requests:
            time.sleep(delay_seconds)

    successful = [r for r in results if r["success"]]
    latencies = [r["time"] for r in successful]

    print("\n" + "=" * 70)
    print("📊 RESULTADOS FINALES")
    print("=" * 70)
    print(f"Peticiones exitosas: {len(successful)} / {total_requests} ({(len(successful)/total_requests)*100:.1f}%)")
    if latencies:
        print(f"Latencia promedio:   {sum(latencies)/len(latencies):.3f} s")
    print("=" * 70)

if __name__ == "__main__":
    # Con 2 segundos de pausa es más que suficiente
    run_paced_test(total_requests=10, delay_seconds=2)