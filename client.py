import socket
import ssl
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from email.mime.base import MIMEBase
from email import encoders
import os

def crear_socket(SERVIDOR_SMTP,PUERTO_SMTP):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVIDOR_SMTP, PUERTO_SMTP))
    return s

def enviar_comando(s, comando):
    s.send(comando.encode('utf-8'))
    respuesta = s.recv(1024).decode('utf-8')
    return respuesta

def autenticar(s, usuario, contraseña):
    usuario_b64 = base64.b64encode(usuario.encode('utf-8')).decode('utf-8')
    contraseña_b64 = base64.b64encode(contraseña.encode('utf-8')).decode('utf-8')
    respuesta = enviar_comando(s, '{}\r\n'.format(usuario_b64))
    if not respuesta.startswith('334'):
        print('Error en la autenticación del usuario.')
        return "Uerror"
    respuesta = enviar_comando(s, '{}\r\n'.format(contraseña_b64))
    if not respuesta.startswith('235'):
        print('Error en la autenticación de la contraseña.')
        return "cerror"
    print('Autenticación exitosa.')
    return "Autenticado"

def enviar_correo(s, remitente, destinatario, asunto, cuerpo, adjunto=None):
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'plain'))

    tempfile = False
    if adjunto is not None:
        if os.path.exists(adjunto):
            filename = adjunto  
        else:
            filename = adjunto.split('/')[-1].split('?')[0]
            resquest = requests.get(adjunto)
            tempfile = True
            with open(filename, 'wb') as f: 
                f.write(resquest.content)
        attachment = open(filename, 'rb')
        nombre_archivo = filename.split('/')[-1]
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename= ' + nombre_archivo)
        msg.attach(part)
        attachment.close()
        if tempfile:
            os.remove(filename)
    try:
        enviar_comando(s, 'MAIL FROM: <{}>\r\n'.format(remitente))
        enviar_comando(s, 'RCPT TO: <{}>\r\n'.format(destinatario))
        enviar_comando(s, 'DATA\r\n')
        enviar_comando(s, msg.as_string() + '\r\n.\r\n')
        return "ce"
        
    except Exception as e:
        print(e) 
        return str(e)