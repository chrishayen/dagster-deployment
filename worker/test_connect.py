"""Test RabbitMQ connection."""
import pika
import os


def test_rabbitmq_connection():
    """Test RabbitMQ connection by creating a queue and sending/receiving a message."""
    # Get connection parameters from environment or use defaults
    broker_url = os.getenv('CELERY_BROKER_URL', 'pyamqp://dagster:dagster@localhost:5672//')

    # Parse the broker URL
    # Format: pyamqp://user:pass@host:port//
    if broker_url.startswith('pyamqp://'):
        broker_url = broker_url.replace('pyamqp://', '')

    # Split credentials and host
    if '@' in broker_url:
        credentials, host_info = broker_url.split('@')
        username, password = credentials.split(':')
    else:
        username = 'dagster'
        password = 'dagster'
        host_info = broker_url

    # Parse host and port
    host_info = host_info.rstrip('/')
    if ':' in host_info:
        host, port = host_info.split(':')
        port = int(port)
    else:
        host = host_info
        port = 5672

    # Create connection
    credentials_obj = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials_obj,
        connection_attempts=3,
        retry_delay=2
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Create a test queue
    queue_name = 'test_queue'
    channel.queue_declare(queue=queue_name, durable=False, auto_delete=True)

    # Send a test message
    test_message = "Hello RabbitMQ! This is a test message."
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=test_message
    )

    # Receive the message
    method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)

    assert method_frame is not None, "No message received from queue"

    received_message = body.decode('utf-8')
    assert received_message == test_message, f"Expected '{test_message}', got '{received_message}'"

    # Clean up
    channel.queue_delete(queue=queue_name)
    connection.close()
