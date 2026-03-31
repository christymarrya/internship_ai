import bcrypt

salt = bcrypt.gensalt()
hashed = bcrypt.hashpw("password".encode("utf-8"), salt)

# Test verification
is_valid = bcrypt.checkpw("password".encode("utf-8"), hashed)
print(f"Password Valid: {is_valid}")
# Test string decoding of hash like in DB
hashed_str = hashed.decode("utf-8")
is_valid_str = bcrypt.checkpw("password".encode("utf-8"), hashed_str.encode("utf-8"))
print(f"Password Valid (str): {is_valid_str}")
