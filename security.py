import bcrypt
def encrypt_pass(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
