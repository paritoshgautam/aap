from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("temporary-pass-123")

    assert hashed != "temporary-pass-123"
    assert verify_password("temporary-pass-123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_roundtrip() -> None:
    token = create_access_token("user-id", {"role": "admin"})

    payload = decode_access_token(token)

    assert payload["sub"] == "user-id"
    assert payload["role"] == "admin"
