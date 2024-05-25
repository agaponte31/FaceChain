from django.shortcuts import render, redirect, get_object_or_404
import FaceRecognition.homomorphic as homo
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
import cv2, shutil, os
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse, HttpResponseForbidden
from PIL import Image, ImageTk
import threading
from django import forms
from .forms import Register, Update, EnableDisable, ManageUsers, CustomUserCreationForm, CustomUserChangeForm, ChangeUserForm
import io, base64
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib.sessions.models import Session
from FaceRecognition.blockchain import contract_address, contract_abi, w3, contract, account_address, private_key, client
from lightphe import LightPHE
from django.contrib.admin.views.decorators import staff_member_required
import numpy as np
from FaceRecognition.external_modules.test import test
import time


start_time = time.time()
end_time = time.time()
logger = logging.getLogger(__name__)


db_dir = "/home/giovanny/django/FaceRecognition/db1"
db_keys = "/home/giovanny/django/FaceRecognition/keys"
tmp_dir = "/home/giovanny/django/FaceRecognition/static/tmp"
latest_frame = None
frame_lock = threading.Lock()

def index(request):
    return redirect('login')

def exit(request):
    logout(request)
    return redirect('home')

@login_required
def home(request):
    is_staff = request.user.is_staff
    if is_staff:
        img_profile = '../static/images/image_user_admin.png'
        profile = 'Administrador'
    else:
        img_profile = '../static/images/image_user.png'
        profile = 'Usuario'
    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']

    if os.path.exists(tmp_dir + "/.tmp.jpg"):
                os.remove(tmp_dir + "/.tmp.jpg")
    if os.path.exists(tmp_dir + "/.tmp.txt"):
                os.remove(tmp_dir + "/.tmp.txt")

    respuesta_msg['is_staff'] = is_staff
    respuesta_msg['img_profile'] = img_profile
    respuesta_msg['profile'] = profile
    return render(request, 'home.html', respuesta_msg)

context_403 = {
            'error_message': 'No tienes permiso para acceder a este recurso.',
            'error_code': '403',
        }

respuesta_msg = {'status': '',
                 'mensaje': '',
                 'nombre': '',
                 'apellido': '',
                 'cedula': '',
                 'error': '',
                 'error_code': ''
                }

@login_required
def validar(request):
    is_staff = request.user.is_staff
    print(is_staff)
    if os.path.exists(tmp_dir + "/.tmp.jpg"):
                os.remove(tmp_dir + "/.tmp.jpg")
    if os.path.exists(tmp_dir + "/.tmp.txt"):
                os.remove(tmp_dir + "/.tmp.txt")

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']

    respuesta_msg['is_staff'] = is_staff
    respuesta_msg['nombre'] = 'validar'           
    return render(request, 'captura_video.html', respuesta_msg)

@login_required
def registrar(request):
    is_staff = request.user.is_staff
    if os.path.exists(tmp_dir + "/.tmp.jpg"):
                os.remove(tmp_dir + "/.tmp.jpg")
    if os.path.exists(tmp_dir + "/.tmp.txt"):
                os.remove(tmp_dir + "/.tmp.txt")

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']

    respuesta_msg['is_staff'] = is_staff
    respuesta_msg['nombre'] = 'registrar'           
    return render(request, 'captura_video.html', respuesta_msg)
    
@login_required
@csrf_exempt
def validar_face(request):
    start_time = time.time()
    is_staff = request.user.is_staff
    if not request.session.get('VALIDAR_SESSION', False):
        # Si no, devuelve un error o redirige
        respuesta_msg['status'] = False
        respuesta_msg['error'] = True
        respuesta_msg['error_code'] = '403'
        respuesta_msg['is_staff'] = is_staff
        respuesta_msg['mensaje'] = 'No tienes permiso para acceder a este recurso.'
        return render(request, 'result.html', respuesta_msg)
    
    del request.session['VALIDAR_SESSION']

    global db_keys
    global tmp_dir
    
    respuesta_msg['error'] = False
    if request.method == 'GET':
        if request.session.get('REGISTER_SESSION', False):
            del request.session['REGISTER_SESSION']

        try:
            image = Image.open(tmp_dir + "/.tmp.jpg")
            image_array = np.array(image)
            print(type(image_array))

            label = test(
                image=image_array,
                model_dir='/home/giovanny/django/FaceRecognition/external_modules/Silent_Face_Anti_Spoofing/resources/anti_spoof_models',
                device_id=0
                )
            print(label)
            if label == 2:
                respuesta_msg['status'] = False
                respuesta_msg['error'] = False
                respuesta_msg['update'] = False
                respuesta_msg['mensaje'] = 'Imagen Falsa, no es un rostro real'
                respuesta_msg['is_staff'] = is_staff
                
                #os.remove(tmp_dir + "/.tmp.jpg")
                return render(request, 'result.html', respuesta_msg)
            
            homo.encrypt_img(tmp_dir, db_keys, ".tmp")
            
        except ValueError:
            #os.remove(static_dir + "/.tmp.jpg")
            #del request.session['OK_REGISTER']
            respuesta_msg['status'] = False
            respuesta_msg['error'] = False
            respuesta_msg['update'] = False
            respuesta_msg['mensaje'] = 'No se detectó ningún rostro'
            respuesta_msg['is_staff'] = is_staff
            
            #os.remove(tmp_dir + "/.tmp.jpg")
            return render(request, 'result.html', respuesta_msg)
            

        else:
            user = homo.recognition(tmp_dir, db_keys)
                   
            if user == False or user['status'] == False:
                print(user)
                respuesta_msg['status'] = False
                respuesta_msg['error'] = False
                respuesta_msg['update'] = False
                respuesta_msg['mensaje'] = 'Usuario no identificado'
                respuesta_msg['is_staff'] = is_staff

                #os.remove(tmp_dir + "/.tmp.jpg")
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f'El proceso tomo {elapsed_time:.4f} segundos')
                return render(request, 'result.html', respuesta_msg)
                    
            else:
                print("Bienvenido " + user['name'])
                print(user['status'])

                respuesta_msg['status'] = True
                respuesta_msg['error'] = False
                respuesta_msg['update'] = False
                respuesta_msg['mensaje'] = 'Usuario encontrado'
                respuesta_msg['nombre'] = 'Nombres: ' + user['name']
                respuesta_msg['apellido'] = 'Apellidos: ' + user['last_name']
                respuesta_msg['cedula'] = 'Cedula: ' + str(user['id_number'])
                respuesta_msg['is_staff'] = is_staff

                #os.remove(tmp_dir + "/.tmp.jpg")
                #del request.session['OK_REGISTER'] 
                
                return render(request, 'result.html', respuesta_msg)

    return redirect('error')

@login_required
@csrf_exempt
def register(request):
    start_time = time.time()
    is_staff = request.user.is_staff
    if not request.session.get('REGISTER_SESSION', False):
        # Si no, devuelve un error o redirige
        respuesta_msg['status'] = False
        respuesta_msg['error'] = True
        respuesta_msg['error_code'] = '403'
        respuesta_msg['is_staff'] = is_staff
        respuesta_msg['mensaje'] = 'No tienes permiso para acceder a este recurso.'
        return render(request, 'result.html', respuesta_msg)
    del request.session['REGISTER_SESSION']
    
    global tmp_dir
    global db_keys
        
    if request.method == 'POST':
        print("entra a escribir1")
        form = Register(request.POST)
        print("entra a escribir2")
        print(form)
        if form.is_valid():
            print("entra a escribir3")

            nombre = form.cleaned_data["text_box"]
            apellido = form.cleaned_data["text_box2"]
            cedula = form.cleaned_data["text_box3"]
            shutil.copyfile(tmp_dir + "/.tmp.jpg", os.path.join(tmp_dir, '{}.jpg'.format(str(cedula))))

            if not os.path.exists(db_keys):
                os.mkdir(db_keys)
                homo.create_keys(db_keys)
               
            res = client.add(tmp_dir + "/" + ".tmp" + ".txt")
            file_cid = res['Hash']
            client.close()

            user_info_encrypt = homo.encrypt_data(name=nombre, last_name=apellido, id_number=cedula)

            # Preparar la transacción
            nonce = w3.eth.get_transaction_count(account_address)
            transaction = contract.functions.addPerson(user_info_encrypt['ciphertext_name'], user_info_encrypt['ciphertext_last_name'], user_info_encrypt['ciphertext_id_number'], file_cid).build_transaction({
                    'chainId': w3.eth.chain_id,
                    'gas': 2000000,
                    'gasPrice': w3.to_wei('50', 'gwei'),
                    'nonce': nonce,
            })

            # Firmar la transacción
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

	        # Enviar la transacción
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

	        # Obtener el recibo de la transacción
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print("Transacción exitosa:", tx_receipt.transactionHash.hex())
    
            print(file_cid)


            #os.remove(tmp_dir + "/" + cedula + ".txt")
            #

            #os.remove(tmp_dir + "/.tmp.jpg")
                  
            #return JsonResponse({'redirect_url': '/respuesta/'})

            respuesta_msg['status'] = True
            respuesta_msg['error'] = False
            respuesta_msg['update'] = False
            respuesta_msg['mensaje'] = 'Usuario registrado satisfactoriamente'
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f'El proceso tomo {elapsed_time:.4f} segundos')
            respuesta_msg['nombre'] = 'Nombres: ' + nombre
            respuesta_msg['apellido'] = 'Apellidos: ' + apellido
            respuesta_msg['cedula'] = 'Cedula: ' + str(cedula)
            respuesta_msg['is_staff'] = is_staff

            if request.session.get('VALIDAR_SESSION', False):
                del request.session['VALIDAR_SESSION']

            return render(request, 'result.html', respuesta_msg)
    
    else:
        if request.session.get('VALIDAR_SESSION', False):
                del request.session['VALIDAR_SESSION']

        print("entra a escribir4")
        try:
            image = Image.open(tmp_dir + "/.tmp.jpg")
            image_array = np.array(image)
            print(type(image_array))

            label = test(
                image=image_array,
                model_dir='/home/giovanny/django/FaceRecognition/external_modules/Silent_Face_Anti_Spoofing/resources/anti_spoof_models',
                device_id=0
                )
            print(label)
            if label == 2:
                respuesta_msg['status'] = False
                respuesta_msg['error'] = False
                respuesta_msg['update'] = False
                respuesta_msg['mensaje'] = 'Imagen Falsa, no es un rostro real'
                respuesta_msg['is_staff'] = is_staff

                #os.remove(tmp_dir + "/.tmp.jpg")
                return render(request, 'result.html', respuesta_msg)

            homo.encrypt_img(tmp_dir, db_keys, ".tmp")

        except ValueError:
            #os.remove(os.path.join(db_dir, '{}.jpg'.format('.tmp')))
            #os.remove(tmp_dir + "/.tmp.jpg")
            respuesta_msg['status'] = False
            respuesta_msg['error'] = False
            respuesta_msg['update'] = False
            respuesta_msg['mensaje'] = 'No se detectó ningún rostro, intente nuevamente'
            respuesta_msg['is_staff'] = is_staff

            return render(request, 'result.html', respuesta_msg)
        else:
            user = homo.recognition(tmp_dir, db_keys)
            print(user)
            if user == False:
                respuesta_msg['status'] = True
                respuesta_msg['error'] = False
                respuesta_msg['update'] = False
                respuesta_msg['is_staff'] = is_staff        
                print("dibuja formulario")
                form = Register()
                respuesta_msg['form'] = form
                request.session['REGISTER_SESSION'] = True

            else:
                respuesta_msg['status'] = True
                respuesta_msg['error'] = False
                respuesta_msg['update'] = False
                respuesta_msg['nombre'] = 'Nombres: ' + user['name']
                respuesta_msg['apellido'] = 'Apellidos: ' + user['last_name']
                respuesta_msg['cedula'] = 'Cedula: ' + str(user['id_number'])
                respuesta_msg['is_staff'] = is_staff
                if user['status'] == False:
                    respuesta_msg['mensaje'] = 'Usuario se encuentra desactivado:'
                else:
                    respuesta_msg['mensaje'] = 'Rostro ya se encuentra resgistrado:'
                
                #os.remove(tmp_dir + "/.tmp.jpg")
                #del request.session['OK_REGISTER'] 
                #return JsonResponse({'redirect_url': '/respuesta/'})
                #if request.session.get('REGISTER_SESSION', False):
                #    del request.session['REGISTER_SESSION']
                return render(request, 'result.html', respuesta_msg)
    
    return render(request, 'register.html', respuesta_msg)

@login_required
@csrf_exempt
def procesar_frame(request):
    
    is_staff = request.user.is_staff      
          
        
    
    global tmp_dir
    if request.method == 'POST':
        
        #request.session['OK_LOGIN'] = True  
        request.session['REGISTER_SESSION'] = True
        request.session['VALIDAR_SESSION'] = True 
        
        data = request.body
        print("procesar")
        # Los datos como JSON, se necesita decodificar el cuerpo de la solicitud.
        import json
        data_dict = json.loads(data)
        imagen_base64 = data_dict.get('imagen', '')
        
        # Verifica si la cadena de la imagen no está vacía
        if imagen_base64:
            format, imgstr = imagen_base64.split(';base64,') 
            image_bytes = base64.b64decode(imgstr)
            
            # Convierte bytes a imagen
            image = Image.open(io.BytesIO(image_bytes))
                       
            try:
                image.save(tmp_dir + '/.tmp.jpg')
                return JsonResponse({'status': 'success'})
            except Exception as e:
                logger.error(f'Ocurrió un error: {e}')
                #return HttpResponse(Error al guardar la imagen.")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            print("No se recibió ninguna imagen.")
            return JsonResponse({'status': 'error', 'message': 'No image data provided.'}, status=400)
    else:
        respuesta_msg['status'] = False
        respuesta_msg['error'] = True
        respuesta_msg['error_code'] = '403'
        respuesta_msg['is_staff'] = is_staff
        respuesta_msg['mensaje'] = 'No tienes permiso para acceder a este recurso.'
        return render(request, 'result.html', respuesta_msg)

@login_required
@csrf_exempt
@staff_member_required(login_url='/error_403/')
def update_query(request):
    is_staff = request.user.is_staff
    if os.path.exists(tmp_dir + "/.tmp.jpg"):
                os.remove(tmp_dir + "/.tmp.jpg")
    if os.path.exists(tmp_dir + "/.tmp.txt"):
                os.remove(tmp_dir + "/.tmp.txt")

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']
    
    global db_keys
    if request.method == 'POST':
        
        form = Update(request.POST)
        
        if form.is_valid():
            cedula = form.cleaned_data["text_box"]
            user_info_encrypt = homo.encrypt_data(id_number=form.cleaned_data["text_box"])
        
            if not os.path.exists(db_keys):
                os.mkdir(db_keys)
                homo.create_keys(db_keys)

            
            # Llamar a una función de lectura
            try:
                person_info_encrypt = contract.functions.getPersonByIdNumber(user_info_encrypt['ciphertext_id_number']).call()

            except:
                respuesta_msg['status'] = False
                respuesta_msg['error'] = False
                respuesta_msg['update'] = True
                respuesta_msg['is_staff'] = is_staff
                respuesta_msg['mensaje'] = 'Usuario no encontrado'
                
                return render(request, 'result.html', respuesta_msg)
            else:
                #print("Información de la Persona:", person_info)

                person_info = homo.decrypt_data(person_info_encrypt[0], person_info_encrypt[1], person_info_encrypt[2])

                form2 = Register(initial = {'text_box': person_info['name'], 'text_box2': person_info['last_name'], 'text_box3': person_info['id_number'], 'oculto': person_info['id_number']})
                respuesta_msg['status'] = True
                respuesta_msg['error'] = False
                respuesta_msg['type'] = 'update_view'
                respuesta_msg['mensaje'] = 'Actualizar datos de ' + person_info['name'] + ' ' + person_info['last_name']
                respuesta_msg['nombre'] = person_info['name'] + ' ' + person_info['last_name']
                respuesta_msg['apellido'] = 'Apellidos: ' + person_info['last_name']
                respuesta_msg['cedula'] = 'Cedula: ' + str(person_info['id_number'])
                respuesta_msg['form'] = form2
                respuesta_msg['is_staff'] = is_staff
                return render(request, 'update_view.html', respuesta_msg)
    
    else:
        print("dibuja formulario1")
        form = Update()
        #request.session['REGISTER_SESSION'] = True
        respuesta_msg['type'] = 'update_query'
        respuesta_msg['mensaje'] = 'Actualizar Datos'
        respuesta_msg['form'] = form
        respuesta_msg['is_staff'] = is_staff
        return render(request, 'update_query.html', respuesta_msg)

@login_required
@csrf_exempt
@staff_member_required(login_url='/error_403/')
def update_view(request):
    is_staff = request.user.is_staff
    respuesta_msg['is_staff'] = is_staff
    if os.path.exists(tmp_dir + "/.tmp.jpg"):
                os.remove(tmp_dir + "/.tmp.jpg")
    if os.path.exists(tmp_dir + "/.tmp.txt"):
                os.remove(tmp_dir + "/.tmp.txt")
    
    global db_keys
    if request.method == 'POST':
        
        form = Register(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['text_box']
            apellido = form.cleaned_data['text_box2']
            cedula_ant = form.cleaned_data['oculto']
            cedula_new = form.cleaned_data['text_box3']

            user_info_encrypt = homo.encrypt_data(name=form.cleaned_data['text_box'], last_name=form.cleaned_data['text_box2'], id_number=form.cleaned_data['oculto'], id_number_new=form.cleaned_data['text_box3'])

            #print(nombre)
            #print(apellido)
            #print(str(cedula_ant))
            #print(str(cedula_new))

            # Preparar la transacción
            nonce = w3.eth.get_transaction_count(account_address)
            transaction = contract.functions.updatePerson(user_info_encrypt['ciphertext_name'], user_info_encrypt['ciphertext_last_name'], user_info_encrypt['ciphertext_id_number'], user_info_encrypt['ciphertext_id_number_new']).build_transaction({
                    'chainId': w3.eth.chain_id,
                    'gas': 2000000,
                    'gasPrice': w3.to_wei('50', 'gwei'),
                    'nonce': nonce,
            })
            
            # Firmar la transacción
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            

	        # Enviar la transacción
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print("POST TRANSACTION")

	        # Obtener el recibo de la transacción
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print("Transacción exitosa:", tx_receipt.transactionHash.hex())

            respuesta_msg['status'] = True
            respuesta_msg['error'] = False
            respuesta_msg['update'] = True
            respuesta_msg['mensaje'] = 'Usuario Modificado'
            respuesta_msg['nombre'] = 'Nombres: ' + form.cleaned_data['text_box']
            respuesta_msg['apellido'] = 'Apellidos: ' + form.cleaned_data['text_box2']
            respuesta_msg['cedula'] = 'Cedula: ' + str(form.cleaned_data['text_box3'])
            #respuesta_msg['cedula_ant'] = 'Cedula anterior: ' + request.POST.get('oculto')
            

    else:
        respuesta_msg['status'] = False
        respuesta_msg['error'] = True
        respuesta_msg['error_code'] = '403'
        respuesta_msg['mensaje'] = 'No tienes permiso para acceder a este recurso.'
        return render(request, 'result.html', respuesta_msg)

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']

    return render(request, 'result.html', respuesta_msg)

@login_required
@csrf_exempt
@staff_member_required(login_url='/error_403/')
def disable_query(request):
    is_staff = request.user.is_staff
    respuesta_msg['is_staff'] = is_staff
    if os.path.exists(tmp_dir + "/.tmp.jpg"):
                os.remove(tmp_dir + "/.tmp.jpg")
    if os.path.exists(tmp_dir + "/.tmp.txt"):
                os.remove(tmp_dir + "/.tmp.txt")

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']
    
    global db_keys
    if request.method == 'POST':
        
        form = Update(request.POST)
        
        if form.is_valid():
            cedula = form.cleaned_data["text_box"]
        
            if not os.path.exists(db_keys):
                os.mkdir(db_keys)
                homo.create_keys(db_keys)

            user_info_encrypt = homo.encrypt_data(id_number=form.cleaned_data["text_box"])
            
            try:
                # Llamar a una función de lectura
                person_info_encrypt = contract.functions.getPersonByIdNumber(user_info_encrypt['ciphertext_id_number']).call()

            except:
                respuesta_msg['status'] = False
                respuesta_msg['error'] = False
                respuesta_msg['update'] = True
                respuesta_msg['mensaje'] = 'Usuario no encontrado'
                
                return render(request, 'result.html', respuesta_msg)
            else:
                person_info = homo.decrypt_data(person_info_encrypt[0], person_info_encrypt[1], person_info_encrypt[2])

                print("Información de la Persona:", person_info)

                respuesta_msg['update'] = True
                respuesta_msg['status'] = True
                respuesta_msg['error'] = False
                respuesta_msg['nombre'] = person_info['name'] + ' ' + person_info['last_name']
                respuesta_msg['apellido'] = 'Apellidos: ' + person_info['last_name']
                respuesta_msg['cedula'] = 'Cedula: ' + str(person_info['id_number'])

                #if person_info[4] == False:
                #  respuesta_msg['mensaje'] = 'Usuario ya se encuentra desactivado'
                #  return render(request, 'result.html', respuesta_msg)  

                form2 = EnableDisable(initial = {'text_box': person_info['name'], 'text_box2': person_info['last_name'], 'text_box3': person_info['id_number'], 'estado': person_info_encrypt[4]})
                                
                respuesta_msg['type'] = 'disable_view'
                respuesta_msg['mensaje'] = 'Usuario: ' + person_info['name'] + ' ' + person_info['last_name']
                
                respuesta_msg['form'] = form2
                return render(request, 'update_view.html', respuesta_msg)
    
    else:
        print("dibuja formulario1")
        form = Update()
        #request.session['REGISTER_SESSION'] = True
        respuesta_msg['type'] = 'disable_query'
        respuesta_msg['mensaje'] = 'Activar/Desactivar Usuario'
        respuesta_msg['form'] = form
        return render(request, 'update_query.html', respuesta_msg)

@login_required
@csrf_exempt
@staff_member_required(login_url='/error_403/')
def disable_view(request):
    is_staff = request.user.is_staff
    respuesta_msg['is_staff'] = is_staff
    if os.path.exists(tmp_dir + "/.tmp.jpg"):
                os.remove(tmp_dir + "/.tmp.jpg")
    if os.path.exists(tmp_dir + "/.tmp.txt"):
                os.remove(tmp_dir + "/.tmp.txt")
    
    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']

    print("Entra a disable_view")
    global db_keys
    if request.method == 'POST':
        form = EnableDisable(request.POST)
        print("Entra a disable_view POST")
        print(form)
        if form.is_valid():
            print("Entra a disable_view form.valid")
            nombre = form.cleaned_data['text_box']
            apellido = form.cleaned_data['text_box2']
            cedula = form.cleaned_data['text_box3']
            estado = form.cleaned_data['estado']
            seleccion = form.cleaned_data['options']

            print(nombre)
            print(apellido)
            print(str(cedula))

            respuesta_msg['update'] = True
            respuesta_msg['status'] = True
            respuesta_msg['error'] = False
            respuesta_msg['nombre'] = 'Nombres: ' + nombre
            respuesta_msg['apellido'] = 'Apellidos: ' + apellido
            respuesta_msg['cedula'] = 'Cedula: ' + str(cedula)
                
            if seleccion == '1' and estado == True:
                
                respuesta_msg['mensaje'] = 'Usuario ya se encuentra activado'
                
            else:
                if seleccion == '2' and estado == False:
                    respuesta_msg['mensaje'] = 'Usuario ya se encuentra desactivado'
                    
                else:
                    # Preparar la transacción
                    user_info_encrypt = homo.encrypt_data(id_number=form.cleaned_data["text_box3"])
                    nonce = w3.eth.get_transaction_count(account_address)
                    
                    if seleccion == '1' and estado == False:
                        transaction = contract.functions.enableDisablePerson(user_info_encrypt['ciphertext_id_number'], True).build_transaction({
                                'chainId': w3.eth.chain_id,
                                'gas': 2000000,
                                'gasPrice': w3.to_wei('50', 'gwei'),
                                'nonce': nonce,
                        })
                        respuesta_msg['mensaje'] = 'Usuario ha sido activado'
                        
                    else:
                        respuesta_msg['mensaje'] = 'Usuario ha sido desactivado'
                        transaction = contract.functions.enableDisablePerson(user_info_encrypt['ciphertext_id_number'], False).build_transaction({
                                'chainId': w3.eth.chain_id,
                                'gas': 2000000,
                                'gasPrice': w3.to_wei('50', 'gwei'),
                                'nonce': nonce,
                        })
                    
                    # Firmar la transacción
                    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
            

	                # Enviar la transacción
                    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                    print("POST TRANSACTION")

	                # Obtener el recibo de la transacción
                    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    print("Transacción exitosa:", tx_receipt.transactionHash.hex())       

            return render(request, 'result.html', respuesta_msg)            

    else:
        respuesta_msg['status'] = False
        respuesta_msg['error'] = True
        respuesta_msg['error_code'] = '403'
        respuesta_msg['mensaje'] = 'No tienes permiso para acceder a este recurso.'
        return render(request, 'result.html', respuesta_msg)

    

    return render(request, 'result.html', respuesta_msg)

# Vista para listar, crear, modificar y eliminar usuarios
@login_required
@staff_member_required(login_url='/error_403/')
def manage_users(request):
    is_staff = request.user.is_staff

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']
        
    respuesta_msg['is_staff'] = is_staff
    if request.method == 'POST':
        form = ManageUsers(request.POST)
                           
        if form.is_valid():
            seleccion = form.cleaned_data['options']

            if seleccion == '1':
                form2 = CustomUserCreationForm()
                respuesta_msg['type'] = 'create'
                respuesta_msg['url'] = 'create_user'
                respuesta_msg['status'] = True
                respuesta_msg['error'] = False
                respuesta_msg['form'] = form2
                respuesta_msg['mensaje'] = 'Crear Usuario: Ingrese datos de usuario'
                return render(request, 'manage_users.html', respuesta_msg)
                
            if seleccion == '2':
                
                users = User.objects.all()
                dynamic_choices = [(user.id, user.username) for user in User.objects.all() if user.username != 'admin']
                print(dynamic_choices)
                form3 = ChangeUserForm()
                form3.fields['select_field'].choices = dynamic_choices                
                print(users)
                respuesta_msg['type'] = 'modify'
                respuesta_msg['url'] = 'modify_user'
                respuesta_msg['status'] = True
                respuesta_msg['error'] = False
                respuesta_msg['form'] = form3
                respuesta_msg['users'] = users
                respuesta_msg['mensaje'] = 'Modificar Usuario'
                return render(request, 'manage_users.html', respuesta_msg)

            if seleccion == '3':

                users = User.objects.all()
                dynamic_choices = [(user.id, user.username) for user in User.objects.all() if user.username != 'admin']
                print(dynamic_choices)
                form4 = ChangeUserForm()
                form4.fields['select_field'].choices = dynamic_choices                
                print(users)
                respuesta_msg['type'] = 'delete'
                respuesta_msg['url'] = 'delete_user'
                respuesta_msg['status'] = True
                respuesta_msg['error'] = False
                respuesta_msg['form'] = form4
                respuesta_msg['users'] = users
                respuesta_msg['mensaje'] = 'Eliminar Usuario'
                return render(request, 'manage_users.html', respuesta_msg)
  
    else:
               
        form = ManageUsers()
        respuesta_msg['type'] = 'manage'
        respuesta_msg['status'] = True
        respuesta_msg['error'] = False
        respuesta_msg['form'] = form
    
    return render(request, 'manage_users.html', respuesta_msg)

@login_required
@staff_member_required(login_url='/error_403/')
def create_user(request):
    is_staff = request.user.is_staff
    respuesta_msg['is_staff'] = is_staff

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']

    if request.method == 'POST':
        form = CustomUserCreationForm()
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            respuesta_msg['status'] = True
            respuesta_msg['error'] = False
            respuesta_msg['update'] = True
            respuesta_msg['mensaje'] = 'Usuario Creado satisfactoriamente'
            return render(request, 'result.html', respuesta_msg)
        
        else:
            respuesta_msg['status'] = True
            respuesta_msg['error'] = False
            respuesta_msg['type'] = 'create'
            respuesta_msg['form'] = form
    else:
        respuesta_msg['status'] = False
        respuesta_msg['error'] = True
        respuesta_msg['error_code'] = '403'
        respuesta_msg['mensaje'] = 'No tienes permiso para acceder a este recurso.'
        return render(request, 'result.html', respuesta_msg)

    return render(request, 'manage_users.html', respuesta_msg)
    
@login_required
@staff_member_required(login_url='/error_403/')
def modify_user(request):
    is_staff = request.user.is_staff
    respuesta_msg['is_staff'] = is_staff

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']

    if request.method == 'POST':
        dynamic_choices = [(user.id, user.username) for user in User.objects.all()]
        form = ChangeUserForm(request.POST)
        form.fields['select_field'].choices = dynamic_choices
        print(form.errors)
        
        if form.is_valid():
            user_id = form.cleaned_data['select_field']
            print(type(user_id))
            name = get_object_or_404(User, pk=user_id)
            print(name)
            form2 = CustomUserChangeForm(initial = {'username': name}, instance=name)
            form2.fields['username'].widget = forms.HiddenInput()
            respuesta_msg['type'] = 'modify_ch'
            respuesta_msg['url'] = 'modify_user_ch'
            respuesta_msg['status'] = True
            respuesta_msg['error'] = False
            respuesta_msg['user_id'] = int(user_id)
            respuesta_msg['form'] = form2
            respuesta_msg['mensaje'] = 'Modificar Usuario ' + str(name)
            return render(request, 'manage_users.html', respuesta_msg)
    else:
        respuesta_msg['status'] = False
        respuesta_msg['error'] = True
        respuesta_msg['error_code'] = '403'
        respuesta_msg['mensaje'] = 'No tienes permiso para acceder a este recurso.'
        return render(request, 'result.html', respuesta_msg)

@login_required
@staff_member_required(login_url='/error_403/')
def modify_user_ch(request, user_id):
    is_staff = request.user.is_staff
    respuesta_msg['is_staff'] = is_staff

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']

    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        form = CustomUserChangeForm(request.POST, instance=user)
        print(form)
        print(user_id)
        
        if form.is_valid():
            form.save()
            respuesta_msg['status'] = True
            respuesta_msg['error'] = False
            respuesta_msg['update'] = True
            respuesta_msg['mensaje'] = 'Usuario ' + str(user) + ' modificado satisfactoriamente'
            return render(request, 'result.html', respuesta_msg)
    else:
        respuesta_msg['status'] = False
        respuesta_msg['error'] = True
        respuesta_msg['error_code'] = '403'
        respuesta_msg['mensaje'] = 'No tienes permiso para acceder a este recurso.'
        return render(request, 'result.html', respuesta_msg)

@login_required
@staff_member_required(login_url='/error_403/')
def delete_user(request):
    is_staff = request.user.is_staff
    respuesta_msg['is_staff'] = is_staff

    if request.session.get('REGISTER_SESSION', False):
        del request.session['REGISTER_SESSION']

    if request.session.get('VALIDAR_SESSION', False):
        del request.session['VALIDAR_SESSION']
        
    if request.method == 'POST':
        dynamic_choices = [(user.id, user.username) for user in User.objects.all()]
        #user = get_object_or_404(User, pk=user_id)
        form = ChangeUserForm(request.POST)
        form.fields['select_field'].choices = dynamic_choices
        print(form)
                
        if form.is_valid():
            user_id = form.cleaned_data['select_field']
            print(type(user_id))
            user = get_object_or_404(User, pk=user_id)
            user.delete()
            respuesta_msg['status'] = True
            respuesta_msg['error'] = False
            respuesta_msg['update'] = True
            respuesta_msg['mensaje'] = 'Usuario ' + str(user) + ' eliminado'
            return render(request, 'result.html', respuesta_msg)
    else:
        respuesta_msg['status'] = False
        respuesta_msg['error'] = True
        respuesta_msg['error_code'] = '403'
        respuesta_msg['mensaje'] = 'No tienes permiso para acceder a este recurso.'
        return render(request, 'result.html', respuesta_msg)
        
    
def error_403(request):
    return render(request, 'error_403.html', {})

def error_401(request):
    return render(request, 'error_401.html', {})

def respuesta(request):
    datos = request.session.get('datos')
    return render(request, 'result.html', datos)