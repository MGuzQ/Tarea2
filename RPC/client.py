from datetime import datetime
import logging
import threading
import grpc
import chat_pb2
import chat_pb2_grpc
import _thread
import sys
import time



def leer():
	while True: 
		responses = stub.Recibir(chat_pb2.Usuario(id=nombre))
		for response in responses:
			print(response.id_em + ": " + response.cuerpo + " [" + response.timestamp + "]")
		
#Parecido al chat route del ejemplo de la pagina, es basicamente la parte que le entrega el stream de mensajes al servidor
def mensajes(msg,dest,ts):
	mensajes = []
	mensajes.append(chat_pb2.Mensaje(id_em = nombre,id_re = str(dest) ,cuerpo = str(msg), timestamp = ts))
	for men in mensajes:
		mensajes.remove(men)
		yield men

def run():
	global nombre
	global channel
	global stub

	channel = grpc.insecure_channel('server:8080')
	stub = chat_pb2_grpc.BroadcastStub(channel)
	

#despliegue "automatico"

	if len(sys.argv)>1 and sys.argv[1] == 'a':
		response = stub.Conectar(chat_pb2.Usuario(id='a'))
		nombre='a'
		
		_thread.start_new_thread(leer,())
		msg=0
		while True:
			msg +=1
			dateTimeObj = datetime.now()
			timestp = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")
			if msg == 5:
				response = stub.Conectados(chat_pb2.Mensaje(id_em = nombre, cuerpo = 'conectados', timestamp = timestp))
				print(response.id_em + ": " + response.cuerpo + "[" + response.timestamp + "]")
			elif msg == 8:
				responses = stub.Enviados(chat_pb2.Usuario(id=nombre))
				for response in responses:
					print(response.cuerpo + " [" + response.timestamp + "]")
			elif msg == 11:
				response = stub.Desconectar(chat_pb2.Usuario(id=nombre))
				exit()
			else:
				resp = stub.Enviar(mensajes(msg,'b',timestp))
			time.sleep(12)


	elif len(sys.argv)>1 and sys.argv[1] == 'b':
		response = stub.Conectar(chat_pb2.Usuario(id='b'))
		nombre = 'b'
		
		_thread.start_new_thread(leer,())
		msg=0
		while True:
			msg +=1
			dateTimeObj = datetime.now()
			timestp = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")
			if msg == 5:
				response = stub.Conectados(chat_pb2.Mensaje(id_em = nombre, cuerpo = 'conectados', timestamp = timestp))
				print(response.id_em + ": " + response.cuerpo + "[" + response.timestamp + "]")
			elif msg == 8:
				responses = stub.Enviados(chat_pb2.Usuario(id=nombre))
				for response in responses:
					print(response.cuerpo + " [" + response.timestamp + "]")
			elif msg == 11:
				response = stub.Desconectar(chat_pb2.Usuario(id=nombre))
				exit()
			else:
				resp = stub.Enviar(mensajes(msg,'a',timestp))
			time.sleep(12)

#----------------------------------------------------
	else:
		while True:

			print("ingrese un nombre de Usuario: ")
			nombre = input()
			response = stub.Conectar(chat_pb2.Usuario(id=nombre))
			if response.msg != "Denegada":
				break
		_thread.start_new_thread(leer,())
		while True:
			msg = input()
			dateTimeObj = datetime.now()
			timestp = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")
			if msg == "conectados":
				response = stub.Conectados(chat_pb2.Mensaje(id_em = nombre, cuerpo = msg, timestamp = timestp))
				print(response.id_em + ": " + response.cuerpo + "[" + response.timestamp + "]")
			elif msg == "enviados":
				responses = stub.Enviados(chat_pb2.Usuario(id=nombre))
				for response in responses:
					print(response.cuerpo + " [" + response.timestamp + "]")
			elif msg == "exit":
				response = stub.Desconectar(chat_pb2.Usuario(id=nombre))
				exit()
			else:
				content = msg.split(":")
				if len(content) >1:
					resp = stub.Enviar(mensajes(content[0],content[1],timestp))
				else:
					print("Error no se puede enviar mensaje")
		 

		
    
if __name__ == '__main__':
    logging.basicConfig()
    print("Para saber los usuarios conectados enviar 'conectados'\nPara ver historial de mensajes enviar 'enviados'\n Para enviar un mensaje a otro usuario enviar 'mensaje:usuario' ")
    run()