from services.auth import hash_password, verify_password, validate_password
def test_hash_verify():
    encoded=hash_password("StrongPassword#123")
    assert encoded!="StrongPassword#123"
    assert verify_password("StrongPassword#123",encoded)
    assert not verify_password("WrongPassword#123",encoded)
def test_policy():
    assert validate_password("short") is not None
    assert validate_password("StrongPassword#123") is None
