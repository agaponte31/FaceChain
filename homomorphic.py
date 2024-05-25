import tenseal as ts # pip install tenseal
import tensorflow
from deepface import DeepFace #!pip install deepface
import base64
import os
from FaceRecognition.blockchain import contract_address, contract_abi, w3, contract, account_address, private_key, client
import ipfshttpclient2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from web3 import Web3


def write_data(file_name, data):
    
    if type(data) == bytes:
        data = base64.b64encode(data)       #bytes to base64
        
    with open(file_name, 'wb') as f: 
        f.write(data)

def read_data(file_name):
    with open(file_name, "rb") as f:
        data = f.read()
    
    #base64 to bytes
    return base64.b64decode(data)

def create_keys(db_keys):
    context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree = 8192,
            coeff_mod_bit_sizes = [60, 40, 40, 60]
          )
    context.generate_galois_keys()
    context.global_scale = 2**40

    secret_context = context.serialize(save_secret_key = True)
    write_data(db_keys + "/secret.txt", secret_context)

    context.make_context_public() #drop the secret_key from the context
    public_context = context.serialize()
    write_data(db_keys + "/public.txt", public_context)

    del context, secret_context, public_context

def encrypt_img(tmp_dir, db_keys, img_file):
    print("ENTRA A ENCRIPT")
    context = ts.context_from(read_data(db_keys + "/secret.txt"))
    img_path = os.path.join(tmp_dir, '{}.jpg'.format(img_file))
    img_embedding = DeepFace.represent(img_path, model_name = 'Facenet')[0]["embedding"]
    enc_v = ts.ckks_vector(context, img_embedding)
    enc_v_proto = enc_v.serialize()
    write_data(os.path.join(tmp_dir, '{}.txt'.format(img_file)), enc_v_proto)

    
    #os.remove(img_path)

    del context, enc_v, enc_v_proto
    

def recognition(tmp_dir, db_keys):
    context = ts.context_from(read_data(db_keys + "/public.txt"))

    #enc_v1_proto = read_data(static_dir + "/.tmp.txt")
    enc_v1_proto = read_data(tmp_dir + "/.tmp.txt")
    
    enc_v1 = ts.lazy_ckks_vector_from(enc_v1_proto)
    enc_v1.link_context(context)

    #print(enc_v1)
    

    num_persons = contract.functions.getNumPersons().call()

    cont = 1
                
    while cont <= num_persons:
        person_info_encrypt = contract.functions.getPersonByIndex(cont).call()

        #print(person_info)
        enc_v2_proto = base64.b64decode(client.cat(person_info_encrypt[3]))
        enc_v2 = ts.lazy_ckks_vector_from(enc_v2_proto)
        enc_v2.link_context(context)
        
        euclidean_squared = enc_v1 - enc_v2
        euclidean_squared = euclidean_squared.dot(euclidean_squared)

        write_data(tmp_dir + "/euclidean_squared.txt", euclidean_squared.serialize())

        del enc_v2_proto, enc_v2, euclidean_squared

        context_dec = ts.context_from(read_data(db_keys + "/secret.txt"))

        euclidean_squared_proto = read_data(tmp_dir + "/euclidean_squared.txt")

        euclidean_squared_dec = ts.lazy_ckks_vector_from(euclidean_squared_proto)
        euclidean_squared_dec.link_context(context_dec)

        euclidean_squared_plain = euclidean_squared_dec.decrypt()[0]
        #print(str(euclidean_squared_plain) + " " + person_info[0])
        print(str(euclidean_squared_plain))

        os.remove(tmp_dir + "/euclidean_squared.txt")

        #euclidean_squared_plain

        if euclidean_squared_plain < 100:
            person_info = decrypt_data(person_info_encrypt[0], person_info_encrypt[1], person_info_encrypt[2])
            user = person_info
            user['status'] = person_info_encrypt[4]
            break
        else:
            user = False
            #print(user)
            
           
        cont += 1

        #print(type(euclidean_squared_plain), euclidean_squared_plain, i)
    
    del enc_v1_proto, enc_v1, euclidean_squared_dec, context, context_dec
    #os.remove(tmp_dir + "/.tmp.txt")
    client.close()
    return user

def new_encryptor(mode):
    # Clave y IV (vector de inicialización)
    key = b'\x00' * 32  # Clave de 256 bits
    iv = b'\x00' * 16   # IV de 128 bits

    # Configurar el cifrador
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    if mode == True:
        return cipher.encryptor()
    if mode == False:
        return cipher.decryptor()

def encrypt_data(id_number, name=False, last_name=False, id_number_new=False):
    
    encryptor_id_number = new_encryptor(True)

    # Añadir padding al mensaje
    id_number_bytes32 = Web3.to_bytes(id_number).ljust(32, b'\0')
    if  name and last_name:
        encryptor_name = new_encryptor(True)
        encryptor_last_name = new_encryptor(True)
        
        name_bytes32 = Web3.to_bytes(text=name).ljust(32, b'\0')
        last_name_bytes32 = Web3.to_bytes(text=last_name).ljust(32, b'\0')
        
        # Cifrar los datos
        user_info_encrypt = {'ciphertext_name': encryptor_name.update(name_bytes32) + encryptor_name.finalize(),
                                'ciphertext_last_name': encryptor_last_name.update(last_name_bytes32) + encryptor_last_name.finalize(),
                                'ciphertext_id_number': encryptor_id_number.update(id_number_bytes32) + encryptor_id_number.finalize()
        }
        if id_number_new:
            encryptor_id_number_new = new_encryptor(True)
            id_number_new_bytes32 = Web3.to_bytes(id_number_new).ljust(32, b'\0')
            user_info_encrypt['ciphertext_id_number_new'] = encryptor_id_number_new.update(id_number_new_bytes32) + encryptor_id_number_new.finalize()
    else:
        user_info_encrypt = {'ciphertext_id_number': encryptor_id_number.update(id_number_bytes32) + encryptor_id_number.finalize()
        }
    return user_info_encrypt

def remove_padding(data_bytes, type_padding):
    # Eliminar ceros a la derecha en los datos de tipo bytes
    if type_padding == True:
        return data_bytes.rstrip(b'\0').decode('utf-8')
    if type_padding == False:
        return data_bytes.rstrip(b'\0')

def decrypt_data(name_encrypt, last_name_encrypt, id_number_encrypt):
    # Configurar el descifrador
    decryptor_name = new_encryptor(False)
    decryptor_last_name = new_encryptor(False)
    decryptor_id_number = new_encryptor(False)

    # Descifrar los datos
    decrypted_padded_data_name = decryptor_name.update(name_encrypt) + decryptor_name.finalize()
    decrypted_padded_data_last_name = decryptor_last_name.update(last_name_encrypt) + decryptor_last_name.finalize()
    decrypted_padded_data_id_number = decryptor_id_number.update(id_number_encrypt) + decryptor_id_number.finalize()

    # Eliminar el padding
    id_number_no_padding = remove_padding(decrypted_padded_data_id_number, False)

    person_info = {'name': remove_padding(decrypted_padded_data_name, True),
                        'last_name': remove_padding(decrypted_padded_data_last_name, True),
                        'id_number': Web3.to_int(id_number_no_padding) 
    }      
    return person_info
