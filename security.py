import bcrypt
def encrypt_pass(password):
    hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hash.decode('utf-8')
