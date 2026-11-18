import asyncio
import json
import re
from dataclasses import dataclass
from time import monotonic
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import get_settings


@dataclass(frozen=True)
class GeocodeResult:
    status: str
    latitude: float | None = None
    longitude: float | None = None
    source: str | None = None


def normalize_address(address: str) -> str:
    return re.sub(r"\s+", " ", address.strip().lower())


class NominatimGeocoder:
    def __init__(self):
        self.cache: dict[str, GeocodeResult] = {}
        self.lock = asyncio.Lock()
        self.last_request_at = 0.0

    async def geocode(self, address: str) -> GeocodeResult:
        key = normalize_address(address)
        if not key:
            return GeocodeResult("nao_encontrado", source="nominatim")
        if key in self.cache:
            return self.cache[key]
        settings = get_settings()
        if settings.geocoder_provider.lower() != "nominatim":
            return GeocodeResult("erro", source=settings.geocoder_provider)
        async with self.lock:
            if key in self.cache:
                return self.cache[key]
            wait = 1 - (monotonic() - self.last_request_at)
            if wait > 0:
                await asyncio.sleep(wait)
            self.last_request_at = monotonic()
            try:
                result = await asyncio.to_thread(self._request, key, settings.geocoder_user_agent)
            except Exception:
                return GeocodeResult("erro", source="nominatim")
            self.cache[key] = result
            return result

    @staticmethod
    def _request(address: str, user_agent: str) -> GeocodeResult:
        query = urlencode({"q": address, "format": "jsonv2", "limit": 1})
        request = Request(f"https://nominatim.openstreetmap.org/search?{query}", headers={"User-Agent": user_agent, "Accept": "application/json"})
        with urlopen(request, timeout=10) as response:
            rows = json.loads(response.read().decode("utf-8"))
        if not rows:
            return GeocodeResult("nao_encontrado", source="nominatim")
        return GeocodeResult("ok", float(rows[0]["lat"]), float(rows[0]["lon"]), "nominatim")


geocoder = NominatimGeocoder()
