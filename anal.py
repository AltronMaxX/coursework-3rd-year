import os
import pandas as pd
import sys
import csv
import math

def analyze_file(file_path):
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{file_path}' не найден.")
        return

    # Попытка прочесть файл с разными кодировками
    try:
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, sep=';', encoding='windows-1251')
        except Exception as e:
            print(f"Не удалось прочитать файл из-за проблем с кодировкой: {e}")
            return
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return

    # Очистка названий колонок от лишних пробелов
    df.columns = [col.strip() for col in df.columns]

    vals = pd.Series([])

    target_col = 'Задержка сигнала (мкс)'

    # Проверка наличия нужной колонки
    if target_col not in df.columns:
        print(f"Ошибка: В файле отсутствует необходимая колонка: '{target_col}'")
        print(f"Доступные колонки: {list(df.columns)}")
        return

    # Преобразование данных в числовой формат (если десятичные дроби записаны через запятую)
    vals = df[target_col].astype(str).str.replace(',', '.').astype(float)
    

    print(f"Файл: {file_path}")
    if len(vals) > 0:
        print(f"Минимальная длительность сигнала: {vals.min():.4f} мкс")
        print(f"Средняя длительность сигналов:     {vals.mean():.4f} мкс")
        print(f"Максимальная длительность сигнала: {vals.max():.4f} мкс")

    print("=" * 60)

def calculate_jitters(file_path, worst_count=10):
    delays = []

    # 1. Чтение файла
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                try:
                    # Убираем возможные пробелы и заменяем запятую на точку
                    val_str = row['Задержка сигнала (мкс)'].replace(',', '.').strip()
                    delays.append(float(val_str))
                except (ValueError, KeyError):
                    continue
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)

    if len(delays) < 1:
        print("Данные отсутствуют.")
        return

    # --- РЕАЛИЗАЦИЯ АЛГОРИТМА ---

    group_size = len(delays)
    actual_worst_count = int(group_size * 0.05)

    # Инициализация массива худших задержек
    worst_latencies = [0.0] * actual_worst_count

    # Поиск N худших значений (алгоритм из вашего примера)
    for current_latency in delays:
        for j in range(actual_worst_count):
            if current_latency > worst_latencies[j]:
                # Сдвиг элементов массива
                for k in range(actual_worst_count - 1, j, -1):
                    worst_latencies[k] = worst_latencies[k-1]
                worst_latencies[j] = current_latency
                break

    # Статистика по худшим значениям
    sum_latency = sum(worst_latencies)
    min_worst = worst_latencies[actual_worst_count - 1]
    max_worst = worst_latencies[0]
    avg_worst = sum_latency / actual_worst_count

    # Расчет Mean Latency для всего массива
    mean_latency = sum(delays) / group_size

    # Расчет RMS Jitter (Standard Deviation)
    sum_squared_diff = sum([(x - mean_latency) ** 2 for x in delays])
    rms_jitter = math.sqrt(sum_squared_diff / group_size)

    # Вывод результатов
    print(f"Worst Latency (Max):        {max_worst:.4f} мкс")
    print(f"Worst Latency (Min):        {min_worst:.4f} мкс")
    print(f"Worst Latency (Average):    {avg_worst:.4f} мкс")


files = [
    "без preempt_rt.csv",
    "без preempt_rt с stress.csv",
    "без preempt_rt с приоритетом.csv",
    "без preempt_rt с приоритетом с stress.csv",
    "preempt_rt.csv",
    "preempt_rt с stress.csv",
    "preempt_rt с приоритетом.csv",
    "preempt_rt с приоритетом с stress.csv"
]
if __name__ == "__main__":
    for i in files:
        analyze_file(i)
        calculate_jitters(i, worst_count=10)
        print()