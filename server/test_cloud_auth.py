import httpx
import asyncio

TOKEN = "663f635b007846009bc399f8cdfaa09c.d0tD87RONQLRh0wb"
URLS = [
    "https://api.antigravity.codes/v1/user",
    "https://api.antigravity.codes/v1/quota",
    "https://api.antigravity.dev/v1/user",
    "https://api.antigravity.dev/v1/quota",
    # Hypothèse: l'IDE communique avec un endpoint Google?
    "https://ide.antigravity.google/v1/user" 
]

async def test():
    async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
        for url in URLS:
             print(f"Testing {url}...")
             headers = {"Authorization": f"Bearer {TOKEN}"}
             try:
                 resp = await client.get(url, headers=headers)
                 print(f"  GET -> {resp.status_code}")
                 print(resp.text[:200])
             except Exception as e:
                 print(f"  Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
