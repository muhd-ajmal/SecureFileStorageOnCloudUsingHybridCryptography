from Crypto.Cipher import AES, PKCS1_OAEP, Blowfish
from Crypto.PublicKey import RSA
from ecies.utils import generate_eth_key
from ecies import encrypt, decrypt
from Crypto.Random import new
from struct import pack
from Crypto.Hash import MD5

def encrypt_aes(data, key):
    length = len(key)
    if 8 <= length <= 16:
        key = key + "0" * (16 - length)
    elif length <= 24:
        key = key + "0" * (24 - length)
    elif length <= 32:
        key = key + "0" * (32 - length)

    key = key.encode('utf-8')
    data = data
    enc = AES.new(key, AES.MODE_EAX)
    nonce = enc.nonce
    enctext, tag = enc.encrypt_and_digest(data)
    return [enctext, tag, nonce]

def rsa_getkeys():
    key_pair = RSA.generate(2048)
    private = key_pair.exportKey().decode('utf-8')
    public = key_pair.publickey().exportKey().decode('utf-8')
    return private, public

def ecc_getkeys():
    key_pair = generate_eth_key()
    private = key_pair.to_hex()
    public = key_pair.public_key.to_hex()
    return private, public


def rsa_encrypt(data, key):
    pubKey = RSA.import_key(key)
    encryptor = PKCS1_OAEP.new(pubKey)
    return encryptor.encrypt(data.encode('utf-8'))

def rsa_decrypt(data, key):
    privKey = RSA.import_key(key)
    decryptor = PKCS1_OAEP.new(privKey)
    key = decryptor.decrypt(data).decode('utf-8')
    print(f"Decryption Key: {key}")
    return key

def aes_decrypt(nonce, tag, data, key):
    length = len(key)
    if 8 <= length <= 16:
        key = key + "0" * (16 - length)
    elif length <= 24:
        key = key + "0" * (24 - length)
    elif length <= 32:
        key = key + "0" * (32 - length)

    key = key.encode('utf-8')
    dec = AES.new(key, AES.MODE_EAX, nonce=nonce)
    try:
        dec_data = dec.decrypt_and_verify(data, tag)
        return dec_data
    except:
        return chr(255)

def ecc_encrypt(data, key):
    data = data.encode('utf-8')
    return encrypt(key, data)

def ecc_decrypt(data, key):
    return decrypt(key, data).decode('utf-8')

def blowfish_encrypt(data, key):
    key = key.encode('utf-8')
    b_size = Blowfish.block_size
    iv = new().read(b_size)
    encryptor = Blowfish.new(key, Blowfish.MODE_CBC, iv)
    plen = b_size - divmod(len(data), b_size)[1]
    padding = [plen] * plen
    padding = pack('b' * plen, *padding)
    encmsg = iv + encryptor.encrypt(data + padding)
    return [encmsg, b_size]

def blowfish_decrypt(data, b_size, key):
    key = key.encode('utf-8')
    iv = data[:b_size]
    decryptor = Blowfish.new(key, Blowfish.MODE_CBC, iv)
    data = data[b_size:]
    decmsg = decryptor.decrypt(data)
    last_byte = decmsg[-1]
    decmsg = decmsg[:- (last_byte if type(last_byte) is int else ord(last_byte))]
    return decmsg

def create_hash(key):
    key = key.encode('utf-8')
    hash_key = MD5.new()
    hash_key.update(key)
    return hash_key.hexdigest()
