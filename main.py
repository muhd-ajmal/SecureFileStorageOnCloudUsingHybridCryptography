import io

from PIL import Image
from cryptography import *
import stegnography as steg
from pickle import load, dump

def encryption(filepath, keypath, key, enctype, extension):
    output = io.BytesIO()
    ftype = ['dat', 'txt', 'csv']
    if enctype == 0:
        try:
            if extension in ftype:
                with open(filepath, "rt") as tfile:
                    data = encrypt_aes(tfile.read().encode('utf-8'), key)
            else:
                with open(filepath, "rb") as tfile:
                    data = encrypt_aes(tfile.read(), key)
            data.extend([extension, enctype])
            dump(data, output)
            return output.getvalue()
        except Exception as ex3:
            print(f"AES Error: {ex3}")
            return chr(260)

    elif enctype in (1, 2):
        try:
            print(keypath)
            img = Image.open(keypath)
            pixels = list(img.getdata())
            pubKey = steg.decode(pixels)
            try:
                if enctype == 1:
                    try:
                        enckey = rsa_encrypt(key, pubKey)
                        if extension in ftype:
                            with open(filepath, "rt") as tfile:
                                data = encrypt_aes(tfile.read().encode('utf-8'), key)
                        else:
                            with open(filepath, "rb") as tfile:
                                data = encrypt_aes(tfile.read(), key)
                        data.extend([extension, enckey, enctype])
                        dump(data, output)
                        return output.getvalue()
                    except:
                        return chr(261)

                elif enctype == 2:
                    try:
                        hkey = create_hash(key)
                        enckey = ecc_encrypt(hkey, pubKey)
                        if extension in ftype:
                            with open(filepath, "rt") as tfile:
                                data = blowfish_encrypt(tfile.read().encode('utf-8'), key)
                        else:
                            with open(filepath, "rb") as tfile:
                                data = blowfish_encrypt(tfile.read(), key)
                        data.extend([extension, enckey, enctype])
                        dump(data, output)
                        return output.getvalue()
                    except:
                        return chr(262)

            except Exception as ex:
                print(f"Conversion Error: {ex}")
                return chr(258)
        except Exception as e:
            print(f"Image Error: {e}")
            return chr(257)
    return

def decryption(filepath, keypath, key):
    ftype = ['dat', 'txt', 'csv']
    with open(filepath, "rb") as file:
        data = load(file)
    try:
        if data[-1] == 0:
            if data[-2] in ftype:
                return (aes_decrypt(data[2], data[1], data[0], key).decode('utf-8'), 'txt')   #data[0] = data, data[1] = nonce, data[2] = tag
            else:
                return (aes_decrypt(data[2], data[1], data[0], key), data[-2])
        else:
            #data[0] = data, data[1] = nonce, data[2] = tag, data[3] = encrypted_type
            #key[0] = encrypted_key, key[1] = private_key
            if data[-1] in (1, 2):
                img = Image.open(keypath)
                pixels = list(img.getdata())
                priKey = steg.decode(pixels)
                if data[-1] == 1:
                    try:
                        keys = rsa_decrypt(data[-2], priKey)
                        if data[-3] in ftype:
                            return aes_decrypt(data[2], data[1], data[0], keys).decode('utf-8'), 'txt'
                        else:
                            return aes_decrypt(data[2], data[1], data[0], keys), data[-3]
                    except Exception as e2:
                        print(f"RSA Key Error: {e2}")
                        return chr(258), chr(258)

                elif data[-1] == 2:
                    try:
                        keys = ecc_decrypt(data[-2], priKey)
                        hkey = create_hash(key)
                        if hkey == keys:
                            if data[-3] in ftype:
                                return blowfish_decrypt(data[0], data[1], key).decode('utf-8'), 'txt'
                            else:
                                return blowfish_decrypt(data[0], data[1], key), data[-3]
                        else:
                            return chr(257), chr(257)
                    except Exception as e2:
                        print(f"ECC Key Error: {e2}")
                        return chr(255), chr(255)
    except Exception as ex:
        print(f"File Error: {ex}")
        return chr(259), chr(259)

def key_generation(imagepath, keytype):
    try:
        private, public = "", ""
        img1 = io.BytesIO()
        img2 = io.BytesIO()
        img, cimg = Image.open(imagepath), Image.open(imagepath)
        pixels = list(img.getdata())
        if keytype == 'RSA':
            private, public = rsa_getkeys()
        elif keytype == 'ECC':
            private, public = ecc_getkeys()
        cimg.putdata(steg.encode(pixels, private))
        cimg.save(img1, format="png")
        cimg.putdata(steg.encode(pixels, public))
        cimg.save(img2, format="png")

        return img1.getvalue(), img2.getvalue()
    except Exception as ex:
        print(f"Key Generation Error: {ex}")

#password contains 16 characters
def developed_and_designed_by(password):
    data = b'\xc3\xf3B8~Q\x10+\xe3\xb4\x99\x94s&\x06\x17od_c\x85'
    tag = b'\xcb\xf8\xb3W\x90\xdc\x91\xbd~\x05\xe3\x90\xe8\xa6\xf7A'
    nonce = b'\x82\xab\x06\x10\xadWs\x95\xa4+\xd6\xc2\x89=Q\xa1'
    print(aes_decrypt(nonce, tag, data, password))