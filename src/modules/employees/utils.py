from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

class Hasher:
    @staticmethod
    def get_password_hash(password) -> str:
        return password_hash.hash(password)
    
    @staticmethod
    def verify_password(password, hashed_password) -> bool:
        return password_hash.verify(password, hashed_password)
