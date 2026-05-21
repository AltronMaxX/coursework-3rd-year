import serial
import csv
import os

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
OUTPUT_FILE = 'arduino_statistics.csv'

if not os.path.exists(SERIAL_PORT):
    print(f"Ошибка: Порт {SERIAL_PORT} не найден.")
    exit(1)

# Переменные для расчета среднего за всё время сессии
total_count = 0
sum_start = 0
sum_end = 0
sum_dur = 0

print(f"Подключение к {SERIAL_PORT}...")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    # Режим 'w' полностью очищает старый файл и гарантирует,
    # что первая строка ВСЕГДА будет содержать наши подписи.
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')

        # Четко размечаем структуру таблицы в первой строке
        headers = [
            'Номер теста',
            'Задержка включения (us)', 'СРЕДНЯЯ задержка включения (us)',
            'Задержка спада (us)', 'СРЕДНЯЯ задержка спада (us)',
            'Длительность ответа (us)', 'СРЕДНЯЯ длительность ответа (us)'
        ]
        writer.writerow(headers)
        file.flush()
        print(f"Файл '{OUTPUT_FILE}' создан. Подписи столбцов внесены в 1-ю строку.")
        print("Ожидаю данные от Arduino... (Нажмите Ctrl+C для остановки)")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()

                # Нам нужны только строки данных, маркер HEADER от Ардуино игнорируем
                if line.startswith("DATA;"):
                    parts = line.split(';')
                    data_row = parts[1:]

                    # Извлекаем текущие показатели
                    test_num = int(data_row[0])
                    start_lat = int(data_row[1])
                    end_lat = int(data_row[2])
                    duration = int(data_row[3])

                    # Инкрементируем метрики для глобального среднего
                    total_count += 1
                    sum_start += start_lat
                    sum_end += end_lat
                    sum_dur += duration

                    # Считаем среднее (актуальное на текущий тест)
                    avg_start = sum_start // total_count
                    avg_end = sum_end // total_count
                    avg_dur = sum_dur // total_count

                    # Собираем строку, где чередуются текущее значение и среднее "за всё время"
                    extended_row = [
                        test_num,
                        start_lat, avg_start,
                        end_lat, avg_end,
                        duration, avg_dur
                    ]

                    # Записываем в CSV и пушим на жесткий диск
                    writer.writerow(extended_row)
                    file.flush()

                    print(f"Успешно записан тест №{test_num} | Текущие средние: "
                          f"Вкл={avg_start}us, Спад={avg_end}us, Длит={avg_dur}us")

                elif line.startswith("DATA_ERROR;"):
                    print("[!] Пропуск итерации: тайм-аут сигнала на стороне Arduino.")

except KeyboardInterrupt:
    print(f"\nСбор данных завершен. Всего тестов обработано: {total_count}. Файл сохранен.")
except PermissionError:
    print(f"\nОшибка прав доступа. Забыли сделать 'sudo chmod 666 {SERIAL_PORT}'?")
except Exception as e:
    print(f"\nКритическая ошибка: {e}")
