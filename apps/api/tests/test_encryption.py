"""Tests for the encryption module (no DB needed)."""

from app.core.encryption import (
    decrypt_secret,
    encrypt_secret,
    generate_dek,
    unwrap_dek,
    wrap_dek,
)


def test_dek_wrap_unwrap():
    dek = generate_dek()
    assert len(dek) == 32
    wrapped = wrap_dek(dek)
    assert wrapped != dek
    unwrapped = unwrap_dek(wrapped)
    assert unwrapped == dek


def test_secret_encrypt_decrypt():
    dek = generate_dek()
    plaintext = "super-secret-api-key-12345"
    ct = encrypt_secret(plaintext, dek)
    assert ct != plaintext.encode()
    result = decrypt_secret(ct, dek)
    assert result == plaintext


def test_different_deks_produce_different_ciphertext():
    dek1 = generate_dek()
    dek2 = generate_dek()
    plaintext = "same-secret"
    ct1 = encrypt_secret(plaintext, dek1)
    ct2 = encrypt_secret(plaintext, dek2)
    assert ct1 != ct2
