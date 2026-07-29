import time

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TTLINK Health API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4321",
        "https://home.ttlink.asia",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

SERVICES = [
    # subs 登录门户已下线（subs.html 返回 404），探测暂时注释；
    # 订阅入口已迁至 home.ttlink.asia/subscribe（Cloudflare Access 保护）
    # {
    #     "id": "subs",
    #     "name": "订阅门户",
    #     "url": "https://subs.ttlink.asia/subs.html",
    #     "probe": True,
    # },
    {
        "id": "cli-proxy-api",
        "name": "CLI Proxy API",
        "url": "https://cli.ttlink.asia/management.html",
        "probe": True,
    },
    {
        "id": "blog",
        "name": "个人博客",
        "url": "https://blog.ttlink.asia",
        "probe": False,
    },
    {
        "id": "smart-notes",
        "name": "智能笔记",
        "url": "https://kb.ttlink.asia/",
        "probe": True,
    },
]


async def probe_service(client: httpx.AsyncClient, service: dict):
    if not service["probe"]:
        return {
            "id": service["id"],
            "name": service["name"],
            "url": service["url"],
            "status": "planned",
            "statusCode": None,
            "latencyMs": None,
        }

    started_at = time.perf_counter()

    try:
        response = await client.get(service["url"])
        latency_ms = round((time.perf_counter() - started_at) * 1000)

        if 200 <= response.status_code < 400:
            status = "up"
        else:
            status = "degraded"

        return {
            "id": service["id"],
            "name": service["name"],
            "url": service["url"],
            "status": status,
            "statusCode": response.status_code,
            "latencyMs": latency_ms,
        }

    except httpx.TimeoutException:
        return {
            "id": service["id"],
            "name": service["name"],
            "url": service["url"],
            "status": "down",
            "statusCode": None,
            "latencyMs": None,
            "error": "timeout",
        }

    except httpx.HTTPError as error:
        return {
            "id": service["id"],
            "name": service["name"],
            "url": service["url"],
            "status": "down",
            "statusCode": None,
            "latencyMs": None,
            "error": str(error),
        }


@app.get("/api/v1/health")
async def get_health():
    timeout = httpx.Timeout(5.0)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        services = []

        for service in SERVICES:
            result = await probe_service(client, service)
            services.append(result)

    has_down_service = any(service["status"] == "down" for service in services)
    has_degraded_service = any(service["status"] == "degraded" for service in services)

    if has_down_service:
        overall_status = "down"
    elif has_degraded_service:
        overall_status = "degraded"
    else:
        overall_status = "ok"

    return {
        "status": overall_status,
        "services": services,
    }