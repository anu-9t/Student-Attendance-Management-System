import pytest

# Hashing passwords properly (PBKDF2) is deliberately slow, and the seed data creates
# a dozen users, so tests use a fast hasher. The one test that checks real hashing
# (SAM-SEC-003) keeps the production setting.
KEEP_REAL_HASHER = {"test_password_is_stored_hashed"}


@pytest.fixture(autouse=True)
def fast_password_hashing(request, settings):
    if request.node.originalname not in KEEP_REAL_HASHER:
        settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
