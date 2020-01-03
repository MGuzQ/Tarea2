from concurrent import futures
import logging
from datetime import datetime
import grpc
import time
import chat_pb2
import chat_pb2_grpc
import os




class ChatServer(chat_pb2_grpc.BroadcastServicer):
	UConectados = set()
	TMensajes = []
	Historial=[]

	def Enviar(self, request_iterator, context):
		
		arch = open("log/log.txt",'a')

		for request in request_iterator:
			self.TMensajes.append(request)
			self.Historial.append(request)
			print(request.id_em+" le ha enviado ("+ request.cuerpo +") a "+request.id_re)
			arch.write(request.id_em+" le ha enviado ("+ request.cuerpo +") a "+request.id_re+' '+request.timestamp + '\n')
		arch.close()
		return chat_pb2.Confirmacion(msg="Enviado")


	def Recibir(self, request, context):
		for men in self.TMensajes:
			if men.id_re == request.id:
				self.TMensajes.remove(men)
				yield chat_pb2.Mensaje(id_em=men.id_em, cuerpo = men.cuerpo, timestamp = men.timestamp)


	def Conectar(self, request, context):
		if request.id in self.UConectados:
			return chat_pb2.Confirmacion(msg="Denegada")
		else:
			self.UConectados.add(request.id)
			print(request.id + " se ha conectado")
			return chat_pb2.Confirmacion(msg="Bienvenido "+ request.id)

	def Conectados(self,request, context):
		dateTimeObj = datetime.now()
		timestp = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")
		return(chat_pb2.Mensaje(id_em = "servidor", cuerpo = str(self.UConectados), timestamp = timestp))

	def Enviados(self, request, context):
		for msg in self.Historial:
			if msg.id_em == request.id:
				yield chat_pb2.Mensaje(id_em=msg.id_em, cuerpo = msg.cuerpo, timestamp = msg.timestamp)

	def Desconectar(self, request, context):
		self.UConectados.remove(request.id)
		print(request.id + " se ha desconectado")
		return chat_pb2.Confirmacion(msg="Bye Bye")




def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_BroadcastServicer_to_server(ChatServer(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
	









