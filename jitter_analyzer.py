import sys
import csv
import math

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
    print(f"Файл: {file_path}")
    print("=== Результаты расчёта (Worst Latency & RMS) ===")
    print(f"Количество записей:         {group_size}")
    print(f"Worst Latency (Max):        {max_worst:.4f} мкс")
    print(f"Worst Latency (Min):        {min_worst:.4f} мкс")
    print(f"Worst Latency (Average):    {avg_worst:.4f} мкс")
    print(f"Mean Latency (Всего):       {mean_latency:.4f} мкс")
    print(f"RMS Jitter (StdDev):        {rms_jitter:.4f} мкс")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python script.py <путь_к_файлу.csv>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    # Можно менять количество учитываемых худших значений здесь:
    calculate_jitters(csv_file_path, worst_count=10)
