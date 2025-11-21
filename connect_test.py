#!/usr/bin/env python3
"""
RabbitMQ connection test script.
Connects to RabbitMQ, creates a queue, sends a message, and receives it.
"""
import pika
import os
import sys


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

    print(f"Connecting to RabbitMQ at {host}:{port} as user '{username}'")

    try:
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

        print("✓ Successfully connected to RabbitMQ")

        # Create a test queue
        queue_name = 'test_queue'
        channel.queue_declare(queue=queue_name, durable=False, auto_delete=True)
        print(f"✓ Created queue: {queue_name}")

        # Send a test message
        test_message = "Hello RabbitMQ! This is a test message."
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=test_message
        )
        print(f"✓ Sent message: {test_message}")

        # Receive the message
        method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)

        if method_frame:
            received_message = body.decode('utf-8')
            print(f"✓ Received message: {received_message}")

            if received_message == test_message:
                print("\n✓ SUCCESS: Message sent and received correctly!")
                success = True
            else:
                print(f"\n✗ ERROR: Received message doesn't match sent message")
                success = False
        else:
            print("\n✗ ERROR: No message received from queue")
            success = False

        # Clean up
        channel.queue_delete(queue=queue_name)
        print(f"✓ Deleted queue: {queue_name}")

        connection.close()
        print("✓ Connection closed")

        return success

    except pika.exceptions.AMQPConnectionError as e:
        print(f"\n✗ ERROR: Failed to connect to RabbitMQ: {e}")
        print("Make sure RabbitMQ is running and accessible")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}: {e}")
        return False


if __name__ == '__main__':
    success = test_rabbitmq_connection()
    sys.exit(0 if success else 1)
