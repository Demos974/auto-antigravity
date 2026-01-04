import httpx
import asyncio

TOKEN = "663f635b007846009bc399f8cdfaa09c.d0tD87RONQLRh0wb"
PORTS = [62538, 9101]
PATHS = ["/exa.language_server_pb.LanguageServerService/GetUserStatus", "/json", "/metrics"]

async def test():
    async with httpx.AsyncClient(verify=False, timeout=2.0) as client:
        for port in PORTS:
             base = f"http://127.0.0.1:{port}"
             print(f"Testing {base}...")
             
             headers_list = [
                 {"Authorization": f"Bearer {TOKEN}"},
                 {"x-api-key": TOKEN},
                 {"x-goog-api-key": TOKEN},
                 {"anthropic-auth-token": TOKEN},
                 {"x-antigravity-token": TOKEN},
             ]
             
             for path in PATHS:
                 url = f"{base}{path}"
                 # Try without headers first
                 try:
                     resp = await client.get(url)
                     print(f"  GET {path} [No Auth] -> {resp.status_code}")
                 except: pass

                 # Try with headers
                 for headers in headers_list:
                     try:
                         # GET
                         resp = await client.get(url, headers=headers)
                         if resp.status_code != 403 and resp.status_code != 404:
                             print(f"  GET {path} [{list(headers.keys())[0]}] -> {resp.status_code} !!!")
                             print(resp.text[:300])
                         
                         # POST (for gRPC)
                         resp = await client.post(url, headers=headers, json={})
                         if resp.status_code != 403 and resp.status_code != 404:
                             print(f"  POST {path} [{list(headers.keys())[0]}] -> {resp.status_code} !!!")
                             print(resp.text[:300])
                             
                     except Exception as e:
                         pass

if __name__ == "__main__":
    asyncio.run(test())
