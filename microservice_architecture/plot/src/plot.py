import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time


def plot_error_distribution():
    # Читаем данные из CSV-файла
    df = pd.read_csv("./logs/metric_log.csv")

    # Выбираем только столбец с абсолютными ошибками
    errors = df["absolute_error"].dropna().astype(float)

    # Создаем график
    plt.figure(figsize=(10, 6))
    sns.histplot(errors, kde=True, bins=30)
    plt.title("Распределение абсолютных ошибок")
    plt.xlabel("Абсолютная ошибка")
    plt.ylabel("Частота")

    # Сохраняем график в файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"./logs/error_distribution_{timestamp}.png"
    plt.savefig(filename)

    print(f"График сохранен как {filename}")


if __name__ == "__main__":
    while True:
        plot_error_distribution()
        time.sleep(60)  # Ожидаем 1 минуту перед следующим обновлением
