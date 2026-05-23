import json
import httpx

from config.config import HEALTH_URL


async def check_server_status() -> tuple[bool, str]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_URL + "/health", timeout=5.0)
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


def make_progress_bar(percent: float, width: int = 10) -> str:
    """Генерирует аккуратный текстовый прогресс-бар."""
    # Защита от некорректных данных
    if isinstance(percent, str) or percent < 0:
        return "░" * width
    filled = int(round((percent / 100) * width))
    return "█" * filled + "░" * (width - filled)


async def check_server_resurse() -> tuple[bool, str]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_URL + "/resurse", timeout=5.0)
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Разбираем метрики из JSON
                    cpu_pct = data.get("cpu", {}).get("usage_percent", 0)
                    
                    ram_data = data.get("ram", {})
                    ram_pct = ram_data.get("usage_percent", 0)
                    ram_used = ram_data.get("used_gb", 0)
                    ram_total = ram_data.get("total_gb", 0)
                    
                    gpu_pct = data.get("gpu", {}).get("usage_percent", 0)
                    
                    bat_data = data.get("battery", {})
                    
                    # Сборка красивого вывода
                    lines = [
                        "📊 <b>Метрики системы:</b>\n",
                        f"💻 <b>CPU:</b> <code>{cpu_pct}%</code>",
                        f"<code>[{make_progress_bar(cpu_pct)}]</code>\n",
                        
                        f"🧠 <b>RAM:</b> <code>{ram_pct}%</code> ({ram_used} / {ram_total} GB)",
                        f"<code>[{make_progress_bar(ram_pct)}]</code>\n"
                    ]
                    
                    # Проверяем графику (если вернулась строка-ошибка или число)
                    if isinstance(gpu_pct, (int, float)):
                        lines.append(f"🎮 <b>GPU Intel:</b> <code>{gpu_pct}%</code>")
                        lines.append(f"<code>[{make_progress_bar(gpu_pct)}]</code>\n")
                    else:
                        lines.append(f"🎮 <b>GPU Intel:</b> <code>н/д</code>\n")
                    
                    # Блок батареи
                    if isinstance(bat_data, dict):
                        bat_pct = bat_data.get("percent", 0)
                        plugged = bat_data.get("power_plugged", False)
                        bat_icon = "🔌" if plugged else "🔋"
                        bat_status = "заряжается" if plugged else "автономно"
                        lines.append(f"{bat_icon} <b>Батарея:</b> <code>{bat_pct}%</code> ({bat_status})\n")
                    
                    # Блок диска (storage)
                    storage_data = data.get("storage", {})
                    if storage_data:
                        st_pct = storage_data.get("usage_percent", 0)
                        st_free = storage_data.get("free_gb", 0)
                        lines.append(f"💾 <b>Диск:</b> свободно <code>{st_free} GB</code> (занято {st_pct}%)")
                    
                    return True, "\n".join(lines)
                    
                except (ValueError, KeyError, TypeError):
                    return True, f"⚠️ Код 200, но ошибка парсинга JSON.\nОтвет: <code>{response.text[:200]}</code>"
            else:
                return (
                    False,
                    f"❌ Сервер вернул код ошибки: <code>{response.status_code}</code>",
                )
                
        except httpx.ConnectTimeout:
            return False, "⏳ Ошибка: Превышено время ожидания (Timeout)."
        except httpx.RequestError as e:
            safe_error = str(e.replace("<", "&lt;").replace(">", "&gt;"))
            return False, f"💥 Ошибка соединения: <code>{safe_error}</code>"
