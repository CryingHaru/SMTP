import PySimpleGUI as sg
from client import *

def main():
    sg.theme('DarkAmber')
    sg.set_options(font=('Times', 12))

    icon = "icon.ico"
    layout = [
        [sg.Text('Servidor:'), sg.InputText('smtp.office365.com', key='host')],
        [sg.Text('Puerto:'), sg.InputText('587', key='puerto')],
        [sg.Text('Usuario:'), sg.InputText('', key='usuario')],
        [sg.Text('Contraseña:'), sg.InputText('', key='contraseña', password_char='*')],
        [sg.Text('Destinatario:'), sg.InputText('', key='destinatario')],
        [sg.Text('Asunto:'), sg.InputText('', key='asunto')],
        [sg.Text('Cuerpo:'), sg.Multiline('', key='cuerpo' , size=(50, 10))],
        [sg.Text('Adjunto:'), sg.InputText('', key='adjunto'), sg.FileBrowse()],
        [sg.Button('Enviar'), sg.Button('Salir')]
    ]

    window = sg.Window('Cliente SMTP', layout,icon=icon)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Salir'):
            break

        if event == 'Enviar':
            host = values['host']
            puerto = int(values['puerto'])
            usuario = values['usuario']
            contraseña = values['contraseña']
            remitente = values['usuario']
            destinatario = values['destinatario']
            asunto = values['asunto']
            cuerpo = values['cuerpo']
            if values['adjunto'] == '':
                adjunto = None
            else:
                adjunto = values['adjunto']

            s = crear_socket(host, puerto)
            s.recv(1024).decode('utf-8')
            enviar_comando(s, 'EHLO Alice\r\n')
            time.sleep(2) 
            respuesta_starttls = enviar_comando(s, 'STARTTLS\r\n')
            if not respuesta_starttls.startswith('220'):
                print('Error al iniciar la conexión segura.')
                break

            context = ssl.create_default_context()
            s = context.wrap_socket(s, server_hostname=host)

            enviar_comando(s, 'EHLO Alice\r\n') 
            enviar_comando(s, 'AUTH LOGIN\r\n')
            auth = autenticar(s, usuario, contraseña)
            if auth == "cerror":
                sg.popup('Error en la autenticación')
            else:
                correo = enviar_correo(s, remitente, destinatario, asunto, cuerpo, adjunto)
                if correo == "ce":
                    sg.popup('Correo enviado con éxito.')
                else:
                    sg.popup('Error al enviar el correo. ' + correo)
                    
                s.close()
                values['destinatario'] = ''
                values['asunto'] = ''
                values['cuerpo'] = ''
                values['adjunto'] = ''

            

    window.close()


main()