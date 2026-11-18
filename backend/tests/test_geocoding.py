import asyncio
from time import monotonic

from app.geocoding import GeocodeResult, NominatimGeocoder


def test_geocoder_caches_normalized_address(monkeypatch):
    geocoder = NominatimGeocoder()
    calls = []

    def request(address, user_agent):
        calls.append(address)
        return GeocodeResult("ok", -10.0, -48.0, "nominatim")

    monkeypatch.setattr(geocoder, "_request", request)
    first = asyncio.run(geocoder.geocode("Rua   A, 10"))
    second = asyncio.run(geocoder.geocode("rua a, 10"))
    assert first == second
    assert calls == ["rua a, 10"]


def test_geocoder_handles_not_found_and_network_error(monkeypatch):
    geocoder = NominatimGeocoder()
    monkeypatch.setattr(geocoder, "_request", lambda *_: GeocodeResult("nao_encontrado", source="nominatim"))
    assert asyncio.run(geocoder.geocode("Endereco inexistente")).status == "nao_encontrado"
    geocoder = NominatimGeocoder()
    monkeypatch.setattr(geocoder, "_request", lambda *_: (_ for _ in ()).throw(OSError("offline")))
    assert asyncio.run(geocoder.geocode("Rua sem rede")).status == "erro"


def test_geocoder_waits_one_second_between_distinct_queries(monkeypatch):
    geocoder = NominatimGeocoder()
    monkeypatch.setattr(geocoder, "_request", lambda *_: GeocodeResult("ok", -10.0, -48.0, "nominatim"))
    asyncio.run(geocoder.geocode("Rua A"))
    started = monotonic()
    asyncio.run(geocoder.geocode("Rua B"))
    assert monotonic() - started >= 0.9
