
import asyncio
import httpx

API_URL = "http://localhost:8080"
ENDPOINTS_TO_TEST = [
    "/",
    "/api",
    "/api/quotas",
    "/api/quota",
    "/api/usage",
    "/api/system",
    "/api/status",
    "/health",
    "/info",
    "/metrics",
    "/api/v1/quotas"
]

async def scan():
    print(f"Scanning {API_URL}...")
    async with httpx.AsyncClient(timeout=2.0) as client:
        for endpoint in ENDPOINTS_TO_TEST:
            url = f"{API_URL}{endpoint}"
            try:
                resp = await client.get(url)
                print(f"GET {url}: {resp.status_code}")
                if resp.status_code == 200:
                    try:
                        print(f"  Body: {resp.json()}")
                    except:
                        print(f"  Body: {resp.text[:100]}...")
            except Exception as e:
                print(f"GET {url}: Failed ({e})")

if __name__ == "__main__":
    asyncio.run(scan())
