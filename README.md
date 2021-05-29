# Bambu
<img src="https://st2.depositphotos.com/6913282/12097/v/600/depositphotos_120975336-stock-illustration-panda-on-a-white-background.jpg" width="400">


## **¿Que es bambu?**
Bambu es un backdoor & troyano para discord, para pruebas y con fines educativos y de entretenimiento.

Bambu Recopila Contraseñas de chrome, token de autenticacion de discord, y con el todos los datos asociados a esa cuenta, ip, y permite ejecutar comandos en la maquina de la victima.
## Interfaz:
Bambu tiene una interfaz extremadamente simple y facil de usar, simplemente en la pagina principal, aparecen todos los usuarios infectados (con su discord tag), y si pulsas en ellos mismos, tendras una interfaz para interactuar con la victima, desde su ip (localizada a traves de la api de google maps), hasta numero de telefono, email, y informacion que se pueda recopilar a traves de discord.

<img src="https://i.ibb.co/S5zzMMQ/imagen.png" width="700">

Tambien integra un backdoor para interactuar con la maquina a traves de una shell, desde la cual podemos ejecutar comandos (primero hay que crear una sesion), donde pueden haber hasta 5 sesiones por defecto de varias personas ejecutando comandos a la vez. Si no os quereis limitar solo a esta shell (que tiene muchos errores y esta un poco bugueada), podeis crear vuestro propio payload con powershell y metasploit y ejecutarlo (siempre que no os pille el av).
## Instalacion:
**Instalacion servidor** 
Bambu es bastante sencillo de usar, aunque aun tiene algunos bugs/errores.
(Testeado en windows)
```bat
C:\Users\artur\Downloads\bambu>pip install -r requirements.txt
C:\Users\artur\Downloads\bambu>python main.py
```
Entonces, el servidor estara en ejecucion (para segundo plano en linux podeis usar `nohup python main.py &`)
Para compilar el cliente, podeis hacerlo de dos formas, con pyinstaller, o pyarmor (el cual recomiendo mas)

**Para instalar pyarmor y compilar:** 
El primer paso es editar el archivo cliente\cliente.py y cambiar la variable SERVER por vuestro servidor:puerto
```bat
C:\Users\artur\Downloads\bambu>pip pyarmor
C:\Users\artur\Downloads\bambu>pyarmor pack cliente\cliente.py -e "--noconsole --onefile"
```
(Las opciones especiales de pyinstaller (`-e "--noconsole --onefile"` son para que se quede en segundo plano el backdoor y se compacte todo en un archivo)
Podreis encontrar el backdoor compilado en cliente\dist
## Proximamente:

- Backdoor con menos errores y la parte del directorio actualizada tambien.
- Boton desde la web para usar la funcion (ya integrada en el codigo) marear, para cambiar el tema durante 60 segundos (en intervalos de 1 segundo) de light a oscuro & el idioma a uno aleatorio.
- Persistencia (hay que trabajar en evadir el AV).

## Configuraciones:
- Las configuraciones se encuentran en el archivo usuarios.ini, donde podemos cambiar tanto el nombre de usuario y contraseña 
(`usuario = admin` y `passwd = ejempla`) de la interfaz web .
- Si aceptas nuevas victimas o no (`backdoor = enabled`), que no afectara a las ya infectadas.
- Cambiar el numero de sesiones que pueden estar ejecutandose hacia un mismo infectado (`max_sessiones_backdoor = 5`).
- Host y puerto en el que se van a ejecutar, se pueden correr tantas instancias en una misma maquina como puertos hayan.