import pika
import json
import os
from dotenv import load_dotenv
from random import randint, choice
from string import ascii_letters
import time

class Publisher:
    def __init__(self):
        load_dotenv()

        self.file_location_exchange = os.environ.get("RABBITMQ_FILE_LOCATION_EXCHANGE")
        self.file_location_queue = os.environ.get("APP_NAME")
        self.host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
        self.port = int(os.environ.get("RABBITMQ_PORT", 5672))
        self.user = os.environ.get("RABBITMQ_USER", "guest")
        self.password = os.environ.get("RABBITMQ_PASSWORD", "guest")

        self.connection = self.connect()
        self.channel = self.connection.channel()

    def connect(self):
        parameters = pika.ConnectionParameters(
            self.host,
            self.port,
            "/",
            pika.PlainCredentials(self.user, self.password)
        )
        return pika.BlockingConnection(parameters)

    def publish_message(self, message):
        self.channel.exchange_declare(exchange=self.file_location_exchange, exchange_type="fanout", durable=True)
        self.channel.queue_declare(queue=self.file_location_queue, durable=True)
        self.channel.queue_bind(exchange=self.file_location_exchange, queue=self.file_location_queue)

        self.channel.basic_publish(exchange=self.file_location_exchange, routing_key='', body=message)

    def close_connection(self):
        self.connection.close()

def generate_complex_message(message_id):
    data = {
        "id": message_id,
        "text": ''.join(choice(ascii_letters) for _ in range(1000)), # large text field
        "numbers": [randint(0, 1000) for _ in range(100)], # list of numbers
        "nested_data": {f"key_{i}": ''.join(choice(ascii_letters) for _ in range(200)) for i in range(50)} # nested data
    }
    return json.dumps(data)

if __name__ == "__main__":
    publisher = Publisher()
    
    try:
        for i in range(500): # Increase the number of messages
            message = generate_complex_message(i)
            publisher.publish_message(message)
            print(f"Message {i} published")
            time.sleep(0.1) # Decrease sleep time to increase frequency
    finally:
        publisher.close_connection()
