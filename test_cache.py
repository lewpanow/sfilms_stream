from database.cache.redis_decorator import cache_aside


# --- Фейковый клиент Redis для примера ---
class FakeRedis:
    def __init__(self): self._cache = {}
    async def get(self, key): return self._cache.get(key)
    async def set(self, key, value, ex): self._cache[key] = value

redis_client = FakeRedis()

# --- Примеры использования ---
@cache_aside(cache_client=redis_client, key_prefix="reports", ttl="5m")
async def generate_report(report_id: int):
    print(f"--- Generating complex report {report_id} ---")
    return {"id": report_id, "data": "..."}

# 2. Кэширование на 30 секунд
@cache_aside(cache_client=redis_client, key_prefix="config", ttl=30)
async def get_config():
    print("--- Reading config from file ---")
    return {"setting": "value"}

# 3. Кэширование НАВСЕГДА (пока кэш не будет очищен вручную)
@cache_aside(cache_client=redis_client, key_prefix="countries")
async def get_country_list():
    print("--- Fetching country list from external API ---")
    return ["USA", "Germany", "France"]

# 4. Неправильный формат вызовет ошибку при старте приложения
try:
    @cache_aside(cache_client=redis_client, key_prefix="test", ttl="1 year")
    async def invalid_ttl_func():
        pass
except ValueError as e:
    print(f"Ошибка при инициализации декоратора: {e}")