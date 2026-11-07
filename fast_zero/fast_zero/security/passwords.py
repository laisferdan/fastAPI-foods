from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _password_hash.verify(plain_password, hashed_password)
