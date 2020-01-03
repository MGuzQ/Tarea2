# Chat RabbitMQ


Para ejecutar esta aplicacion lo primero es ejecutar docker-compose build, para que se creen los containers. Luego para ejecutar el servidor y los clientes "automaticos" se debe usar docker-compose up. Finalmente para ejecutar un nuevo cliente se usa el comando docker-compose run client bash y una vez al interior del container ejecutar python3 client.py

El log de los mensajes enviados estan en la carpeta historia.

Para evitar error de conexion, esperar a que el servicio de rabbitmq anuncie que se ha desplegado en la consola que se ejecuto docker-compose up. Es por esto que el servidor y los clientes "automaticos" llevan un sleep(45) para esperar a que el servicio se termine de levantar.
