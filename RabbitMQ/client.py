import pika
import _thread
from datetime import datetime
import sys
import time

if len(sys.argv)>1:
	print ("Esperando a que el servicio se levante...")
	time.sleep(45)

#funcion que se usara para hacer "lectura" de mensajes en un nuevo thread
#se crea una nueva conexion debido a que pika tiene un error al momento de usar la misma conexion en un nuevo thread
#este error tiende a aparecer cuando se usa la version "automatica" del codigo y no la manual. Nose por que.
ip='rabbitmq'
def leer ():
	connection2 = pika.BlockingConnection(pika.ConnectionParameters(ip))
	channel2 = connection2.channel()
	channel2.exchange_declare(exchange='direct_logs', exchange_type='direct')
	result = channel2.queue_declare(queue='', exclusive=True)
	queue_name = result.method.queue
	channel2.queue_bind(exchange='direct_logs', queue=queue_name, routing_key=nombre)
	channel2.basic_consume(queue=queue_name, on_message_callback=recibir, auto_ack=True)
	channel2.start_consuming()
	
#funcion que se usara para enviar mensajes al servidor
def enviar(rk, msg):
	channel.basic_publish(
    exchange='',
    routing_key=rk,
    body=msg)


connection = pika.BlockingConnection(
    pika.ConnectionParameters(ip))
channel = connection.channel()

#channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

channel.queue_declare(queue='ta_qu', durable=True)

channel.queue_declare(queue='cliente', durable=True)

#Se le avisa al servidor que llego un nuevo cliente
enviar("ta_qu","Hola Servidor")
#print(" [x] Sent %r" % "Hola Servidor")

#funcion que se usa para iniciar la conexion con el servidor
def conectar(ch, method, properties, body):
	cbody = body.decode('UTF-8')
	conectado = 0

	global nombre

# para los 2 clientes inciales
	if len(sys.argv) > 1 and sys.argv[1] == 'a':
		nombre = 'a'
		enviar('ta_qu', nombre + '.---.con')
		channel.stop_consuming()
	
	elif len(sys.argv) > 1 and sys.argv[1] == 'b':
		nombre = 'b'
		enviar('ta_qu', nombre + '.---.con')
		channel.stop_consuming()
#----------------------------------------------------
	else:
		while conectado != 1:
			print("Ingrese nombre de usuario:")
			inp = input()
			UConectados = eval(cbody)
			if inp not in UConectados:
				enviar("ta_qu", inp + '.---.con')
				conectado = 1
				nombre = inp
				channel.stop_consuming()
			else:
				print("Nombre no disponible")
	
#funcion usada para recibir los mensajes que el servidor envia
def recibir(ch, method, properties, body):
	cbody = body.decode('UTF-8')
	content = cbody.split(':')
	print("[x] %r:%r" % (content[0], content[1]))


channel.basic_consume(queue="cliente", on_message_callback=conectar, auto_ack=True)
print("Conectando con el servidor...")
channel.start_consuming()

'''result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key=nombre)
channel.basic_consume(queue=queue_name, on_message_callback=recibir, auto_ack=True)'''

_thread.start_new_thread(leer,())

k = 0
re = ''
print("Para enviar un mensaje debe escribir 'msg:receptor\nPara ver los usuarios conectados escribir 'conectados'\nPara ver los mensajes enviados escribir 'enviados'\nY para salir 'exit' ")
while True:
	if len(sys.argv) > 1 :
		if sys.argv[1] == 'a':
			re = 'b'
		else:
			re = 'a'

		k += 1
		time.sleep(2)
		dateTimeObj = datetime.now()
		timestp = dateTimeObj.strftime("%d-%b-%Y %H.%M.%S")
		
		if k == 6:
			tosend = 'conectados'
			enviar("ta_qu",nombre+":"+tosend + ': ['+timestp+']')
		elif k == 9:
			tosend = 'enviados'
			enviar("ta_qu",nombre+":"+tosend + ': ['+timestp+']')
		elif k == 11:
			tosend = 'exit'
			enviar("ta_qu",nombre+":"+tosend + ': ['+timestp+']')
			exit()
		else:
			tosend = str(k)+':'+re
			enviar("ta_qu",nombre+":"+tosend + ': ['+timestp+']')
		time.sleep(6)

	else:
		tosend = input()
		dateTimeObj = datetime.now()
		timestp = dateTimeObj.strftime("%d-%b-%Y %H.%M.%S")
		enviar("ta_qu",nombre+":"+tosend + ': ['+timestp+']')
		if tosend == 'exit':
			exit()

#connection.close()