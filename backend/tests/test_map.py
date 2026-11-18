from datetime import date
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.auth import get_current_user
from app import models


def test_map_filters_status_and_returns_missing_locations():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    seller = models.Seller(name="Vendedor", phone="5599999999999")
    session.add(seller); session.flush()
    sale = models.Sale(seller_id=seller.id, customer_name="Cliente", payment_method="pix", status="confirmada")
    session.add(sale); session.flush()
    manifest = models.DeliveryManifest(code="ROM-1", delivery_date=date(2026, 11, 18), driver_name="Motorista", status="preparacao")
    manifest.items = [
        models.DeliveryManifestItem(sale_id=sale.id, delivery_address="Rua A", delivery_order=1, status="entregue", latitude=-10.1, longitude=-48.1, geocode_status="ok"),
        models.DeliveryManifestItem(sale_id=sale.id, delivery_address="Rua B", delivery_order=2, status="pendente", geocode_status="pendente"),
    ]
    session.add(manifest); session.commit()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="admin", access_roles=[], permission_overrides=[])
    try:
        response = TestClient(app).get("/api/mapa/entregas?date=2026-11-18&status=entregue")
        assert response.status_code == 200
        assert len(response.json()["points"]) == 1
        response = TestClient(app).get("/api/mapa/entregas?date=2026-11-18&status=todos")
        assert len(response.json()["without_location"]) == 1
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="vendedor", access_roles=[], permission_overrides=[])
        assert TestClient(app).get("/api/mapa/entregas?date=2026-11-18").status_code == 403
    finally:
        app.dependency_overrides.clear()
        session.close()
