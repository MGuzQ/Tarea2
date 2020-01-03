import pika
import os
import time

print("Esperando a que el servicio se levante...")
time.sleep(45)


#se usa para la comunicacion con los nuevos clientes que van entrando
ip = 'rabbitmq'
def enviar(rk, msg):
	channel.basic_publish(
    exchange='',
    routing_key=rk,
    body=msg)

#se usa para la comunicacion con los clientes que ya adquirieron un nombre
def enviarm (rk, msg):
	channel.basic_publish(
    exchange='direct_logs',
    routing_key=rk,
    body=msg)

connection = pika.BlockingConnection(pika.ConnectionParameters(ip))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

channel.queue_declare(queue='ta_qu', durable=True)
#print(' [*] Waiting for messages. To exit press CTRL+C')

#para guardar los usuarios conectados y los mensajes que ha enviado durante su conexion un cliente
UConectados = []
TMensajes = dict()



#funcion que se usa para recibir los mensajes enviados por los clientes
def callback(ch, method, properties, body):
	cbody = body.decode('UTF-8')
	content = cbody.split(":")

	#abrir archivo
	arch = open("log/log.txt",'a')

	#este if es donde se reciben los mensajes y se redirigen al destinatario		
	if len(content) > 3:
		em,msg,dest,tms = content
		ch.basic_ack(delivery_tag=method.delivery_tag)
		enviarm(dest,em+":"+msg+tms)
		TMensajes[em].append(dest+":"+msg+tms)
		print("%r le ha enviado un mensaje a %r" %(em,dest))
		arch.write(em+" le ha enviado ("+ msg +") a "+dest+' '+tms + '\n')
		arch.close()

	#aqui se procesan las "funciones" de ver usuarios conectados, ver mensajes enviados y desconectarse
	elif len(content) > 2:
		em,msg, tms = content

		#simplemente se envia la lista de usuarios conectados
		if msg == 'conectados':
			enviarm(em,'servidor:'+str(UConectados))
			ch.basic_ack(delivery_tag=method.delivery_tag)
			print("Enviando lista de conectados a %r" %em)
		#se recorre el diccionario que contiene los mensajes enviados por un usuario con sus respectivos destinatarios
		elif msg == 'enviados':
			ch.basic_ack(delivery_tag=method.delivery_tag)
			print("Enviando los historial de mensajes a %r" %em)
			for men in TMensajes[em]:
				dec = men.split(':')
				enviarm(em,'servidor: Para='+dec[0]+" "+dec[1])
				
		#al momento en que el usuario se desconecta, se borra de la lista de conectados y se limpia los mensajes enviados de la sesion cerrada
		elif msg == 'exit':
			channel.queue_purge('cliente')
			UConectados.remove(em)
			del TMensajes[em]
			print("%r se ha desconectado" %em)
			enviar('cliente', str(UConectados))
			ch.basic_ack(delivery_tag=method.delivery_tag)
		else:
			ch.basic_ack(delivery_tag=method.delivery_tag)
			enviarm(em,'servidor: ??')





	#aqui es donde se "genera" la conexion del usuario, funciona de manera bloqueante para asegurar que el nombre de usuario sea unico
	else:
		
		ch.basic_ack(delivery_tag=method.delivery_tag)
		cont = cbody.split(".---.")
		#aqui se "desbloquea" la opcion de conectarse para otros usuarios que esten en "espera" para la conexion con el servidor
		if len(cont) > 1 and cont[1] == 'con':
			UConectados.append(cont[0])
			TMensajes[cont[0]] = []
			enviar("cliente",str(UConectados))
			print("[*] Se conecto:%r" %cont[0] )
		


channel.basic_consume(queue='ta_qu', on_message_callback=callback)
#al primer cliente que se intente conectar, inmediatamente se le entregara una lista vacia ya que no hay usuarios conectados
enviar("cliente",str(UConectados))
print("Esperando usuarios...")
channel.start_consuming()