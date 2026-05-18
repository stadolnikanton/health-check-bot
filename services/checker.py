import json

import httpx

from config.config import HEALTH_URL


async def check_server_status() -> tuple[bool, str]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_URL, timeout=5.0)
            if response.status_code == 200:
                try:
                    data = response.json()
                    return (
                        True,
                        f"Код: 200\nДанные: <pre><code>{json.dumps(data, ensure_ascii=False)}</code></pre>",
                    )
                except ValueError:
                    return True, f"Код: 200\nОтвет: <code>{response.text}</code>"
            else:
                return (
                    False,
                    f"Сервер вернул код ошибки: <code>{response.status_code}</code>",
                )
        except httpx.ConnectTimeout:
            return False, "Ошибка: Превышено время ожидания (Timeout)."
        except httpx.RequestError as e:
            safe_error = str(e).replace("<", "&lt;").replace(">", "&gt;")
            return False, f"Ошибка соединения: <code>{safe_error}</code>"
