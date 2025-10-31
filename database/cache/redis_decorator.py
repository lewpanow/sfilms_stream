import json
import hashlib
from functools import wraps
from typing import Callable, Any, Union

import re
from typing import Union


def _parse_ttl(ttl: Union[int, str, None]) -> Union[int, None]:
    if ttl is None:
        return None

    if isinstance(ttl, int):
        if ttl <= 0:
            raise ValueError("TTL должно быть положительным числом")
        return ttl

    if isinstance(ttl, str):
        match = re.fullmatch(r"(\d+)\s*([a-z]+)", ttl.lower())
        if not match:
            raise ValueError(f"Неверный формат TTL строки: '{ttl}'.")

        value, unit_str = int(match.group(1)), match.group(2)

        if unit_str.startswith('s'):  # second, seconds, s
            return value
        if unit_str.startswith('m'):  # minute, minutes, m
            return value * 60
        if unit_str.startswith('h'):  # hour, hours, h
            return value * 3600
        if unit_str.startswith('d'):  # day, days, d
            return value * 86400

        raise ValueError(f"Неизвестная единица измерения времени в TTL: '{unit_str}'")

def cache_aside(
        cache_client: Any,
        key_prefix: str,
        ttl: Union[int, str, None] = None,
        serializer: Callable = json.dumps,
        deserializer: Callable = json.loads,
        condition_fn: Callable[[Any], bool] = lambda result: result is not None
):
    ttl_in_seconds = _parse_ttl(ttl)

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            args_for_key = args[1:] if (args and hasattr(args[0], func.__name__)) else args
            key_suffix_str = json.dumps((args_for_key, kwargs), sort_keys=True, default=str)
            key_suffix_hash = hashlib.md5(key_suffix_str.encode()).hexdigest()
            cache_key = f"{key_prefix}:{func.__name__}:{key_suffix_hash}"

            force_refresh = kwargs.pop("force_refresh", False)

            if not force_refresh:
                cached_value = await cache_client.get(cache_key)
                if cached_value:
                    print(f"CACHE HIT for key: {cache_key}")
                    return deserializer(cached_value)

            print(f"CACHE MISS for key: {cache_key}")
            result = await func(*args, **kwargs)

            if condition_fn(result):
                serialized_result = serializer(result)
                await cache_client.set(cache_key, serialized_result, ex=ttl_in_seconds)
                ttl_log = f"TTL: {ttl}" if ttl is not None else "TTL: forever"
                print(f"CACHED result for key: {cache_key} with {ttl_log}")

            return result

        return wrapper

    return decorator
