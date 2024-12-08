import pika
import pickle
import json
import numpy as np

# Читаем файл с сериализованной моделью
with open("myfile.pkl", "rb") as pkl_file:
    regressor = pickle.load(pkl_file)

try:
    # Создаём подключение по адресу rabbitmq:
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()

    # Объявляем очередь features
    channel.queue_declare(queue="features")
    # Объявляем очередь y_pred
    channel.queue_declare(queue="y_pred")

    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        print(f"Получен вектор признаков {body}")
        features = json.loads(body)
        pred = regressor.predict(
            np.array([float(v) for v in features["body"]]).reshape(1, -1)
        )
        result = {"id": features["id"], "body": pred[0]}
        channel.basic_publish(
            exchange="", routing_key="y_pred", body=json.dumps(result)
        )
        print(f"Предсказание {pred[0]} отправлено в очередь (ID: {features['id']})")

    # Извлекаем сообщение из очереди features
    channel.basic_consume(queue="features", on_message_callback=callback, auto_ack=True)
    print("...Ожидание сообщений")

    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()
except Exception as e:
    print(f"Ошибка: {e}")
    print("Не удалось подключиться к очереди")
