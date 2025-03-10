'''Password hashing'''

from passlib.context import CryptContext

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)


def generate_pswd_hash(plain_password):
    return pwd_context.hash(plain_password)


def check_pswd_hash(plain_password, hashed):
    return pwd_context.verify(plain_password, hashed)
