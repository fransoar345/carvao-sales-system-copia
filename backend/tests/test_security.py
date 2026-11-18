import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.auth import get_current_user
from app.database import Base, get_db
from app.main import app, login_attempts
from app.schemas import AccessUserCreate, SellerCreate, SellerUpdate
from app.seed import seed_data


class MissingUserQuery:
    def options(self, *args):
        return self

    def filter(self, *args):
        return self

    def first(self):
        return None


class MissingUserDatabase:
    def query(self, *args):
        return MissingUserQuery()


@pytest.fixture(autouse=True)
def reset_security_state():
    login_attempts.clear()
    app.dependency_overrides.clear()
    yield
    login_attempts.clear()
    app.dependency_overrides.clear()


def test_login_is_rate_limited_after_five_failed_attempts():
    app.dependency_overrides[get_db] = lambda: MissingUserDatabase()
    client = TestClient(app)
    payload = {"username": "nao-existe@example.com", "password": "senha-incorreta"}

    for _ in range(5):
        response = client.post("/api/auth/login", data=payload)
        assert response.status_code == 401
        assert response.json()["detail"] == "Credenciais invalidas"

    response = client.post("/api/auth/login", data=payload)
    assert response.status_code == 429


@pytest.mark.parametrize("role", ["vendedor", "gerente"])
@pytest.mark.parametrize("endpoint", ["/api/dono/resumo", "/api/dono/vendas-por-dia", "/api/dono/vendedores", "/api/dono/clientes"])
def test_owner_routes_deny_seller_and_manager(role, endpoint):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role=role)
    app.dependency_overrides[get_db] = lambda: SimpleNamespace()

    response = TestClient(app).get(endpoint)
    assert response.status_code == 403


def test_app_refuses_to_start_without_jwt_secret(tmp_path):
    backend_dir = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment.pop("JWT_SECRET", None)
    environment["PYTHONPATH"] = str(backend_dir)
    environment["CORS_ORIGINS"] = "http://testserver"
    result = subprocess.run(
        [sys.executable, "-c", "from app.config import get_settings; get_settings()"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "JWT_SECRET e obrigatoria" in result.stderr


@pytest.mark.parametrize(
    "factory, payload",
    [
        (AccessUserCreate, {"name": "Teste", "email": "teste@example.com", "password": "admin123456", "role_ids": [1]}),
        (SellerCreate, {"name": "Teste", "phone": "5599999999999", "email": "teste@example.com", "temporary_password": "1234567890"}),
        (SellerUpdate, {"new_password": "vendedor123"}),
    ],
)
def test_weak_passwords_are_rejected(factory, payload):
    with pytest.raises(ValidationError):
        factory(**payload)


def test_seed_does_not_create_demo_users_by_default(monkeypatch):
    monkeypatch.delenv("SEED_DEMO", raising=False)
    monkeypatch.setenv("ADMIN_INITIAL_PASSWORD", "Senha-forte-2026")
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    seed_data(session)

    assert session.query(models.User).count() == 1
    assert session.query(models.Seller).count() == 0
