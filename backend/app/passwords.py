COMMON_PASSWORDS = frozenset({
    "123456", "12345678", "123456789", "1234567890", "password", "senha123",
    "senha1234", "admin123", "admin1234", "admin12345", "admin123456",
    "gerente123", "gerente1234", "gerente12345", "gerente123456",
    "vendedor123", "vendedor1234", "vendedor12345", "vendedor123456",
})


def validate_password_strength(password: str) -> str:
    if len(password) < 10:
        raise ValueError("A senha deve ter no minimo 10 caracteres.")
    if password.strip().lower() in COMMON_PASSWORDS:
        raise ValueError("Escolha uma senha que nao seja comum.")
    return password
