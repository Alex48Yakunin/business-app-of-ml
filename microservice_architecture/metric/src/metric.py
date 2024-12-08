import pika
import json
import csv


def write_to_csv(row):
    with open("./logs/metric_log.csv", "a", newline="") as csvfile:
        fieldnames = ["id", "y_true", "y_pred", "absolute_error"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow(row)


def calculate_absolute_error(y_true, y_pred):
    return abs(y_true - y_pred)


def callback(ch, method, properties, body):
    data = json.loads(body)

    # Сохраним полученные данные
    write_to_csv(
        {
            "id": data["id"],
            "y_true": data["body"],
            "y_pred": None,
            "absolute_error": None,
        }
    )

    print(f"Получено сообщение из очереди {method.routing_key}: {data}")

    if method.routing_key == "y_true":
        print("Ожидание сообщения из очереди y_pred...")

        y_pred_data = {"id": data["id"], "body": 123.45}
        write_to_csv(
            {
                "id": data["id"],
                "y_true": data["body"],
                "y_pred": y_pred_data["body"],
                "absolute_error": calculate_absolute_error(
                    data["body"], y_pred_data["body"]
                ),
            }
        )

        print(
            f"Вычислена абсолютная ошибка: {calculate_absolute_error(data['body'], y_pred_data['body'])}"
        )

    ch.basic_ack(delivery_tag=method.delivery_tag)


try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
    channel = connection.channel()

    channel.queue_declare(queue="y_true")
    channel.queue_declare(queue="y_pred")

    print("Соединение с RabbitMQ установлено...")
    print("Ожидание сообщений...")

    channel.basic_consume(queue="y_true", on_message_callback=callback, auto_ack=False)

    channel.start_consuming()

except Exception as e:
    print(f"Ошибка: {e}")
