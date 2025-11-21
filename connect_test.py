#!/usr/bin/env python3
"""
RabbitMQ connection test script.
Connects to RabbitMQ, creates a queue, sends a message, and receives it.
"""
import pika
import os
import sys
import json
import ssl


def test_rabbitmq_connection():
    """Test RabbitMQ connection by creating a queue and sending/receiving a message."""

    # Get connection parameters from environment variables
    connection_url = os.getenv('APP_CONFIG_BROKER_CONNECTION_URL')
    username = os.getenv('APP_CONFIG_BROKER_CONNECTION_LOGIN')
    password = os.getenv('APP_CONFIG_BROKER_CONNECTION_PASSWORD')
    ssl_options_str = os.getenv('APP_CONFIG_BROKER_CONNECTION_SSL_OPTIONS')

    # Fallback to defaults if not provided
    if not connection_url:
        connection_url = 'https://localhost:5672/'
    if not username:
        username = 'dagster'
    if not password:
        password = 'dagster'

    # Parse connection URL
    # Format: https://host:port/
    connection_url = connection_url.rstrip('/')

    # Remove protocol prefix
    if '://' in connection_url:
        protocol, host_info = connection_url.split('://', 1)
        use_ssl = protocol == 'https'
    else:
        host_info = connection_url
        use_ssl = False

    # Parse host and port
    if ':' in host_info:
        host, port = host_info.rsplit(':', 1)
        port = int(port)
    else:
        host = host_info
        port = 5671 if use_ssl else 5672

    # Parse SSL options
    ssl_context = None
    if ssl_options_str:
        ssl_options = json.loads(ssl_options_str)
        if use_ssl and 'cafile' in ssl_options:
            ssl_context = ssl.create_default_context(cafile=ssl_options['cafile'])

    print(f"Connecting to RabbitMQ at {host}:{port} as user '{username}' (SSL: {use_ssl})")

    try:
        # Create connection
        credentials_obj = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials_obj,
            ssl_options=pika.SSLOptions(ssl_context) if ssl_context else None,
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
