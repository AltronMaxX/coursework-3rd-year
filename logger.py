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

need_tests = 3000

print(f"Подключение к {SERIAL_PORT}...")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    if os.path.exists(OUTPUT_FILE):
        print("Файл" + OUTPUT_FILE + "уже существует!")
        exit(0)

    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')

        # Размечаем структуру таблицы в первой строке
        headers = [
            'Номер теста',
            'Задержка сигнала (мкс)', 
            'СРЕДНЯЯ задержка сигнала (мкс)'
        ]
        writer.writerow(headers)
        file.flush()
        print(f"Файл '{OUTPUT_FILE}' создан. Подписи столбцов внесены в 1-ю строку.")
        print("Ожидаю данные от Arduino... (Нажмите Ctrl+C для остановки)")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()

                if line.startswith("DATA;"):
                    parts = line.split(';')
                    data_row = parts[1:]

                    # Извлекаем текущие показатели
                    test_num = int(data_row[0])
                    lat = int(data_row[1])

                    # Инкрементируем метрики для глобального среднего
                    total_count += 1
                    sum_start += lat

                    # Считаем среднее (актуальное на текущий тест)
                    avg_start = sum_start // total_count

                    # Собираем строку, где чередуются текущее значение и среднее "за всё время"
                    extended_row = [
                        test_num,
                        lat, 
                        avg_start
                    ]

                    # Записываем в CSV и пушим на жесткий диск
                    writer.writerow(extended_row)
                    file.flush()

                    print(f"Успешно записан тест №{test_num} | Текущие средние: "
                          f"Сигнал={avg_start}мкс")

                    if need_tests == test_num:
                        print("Успешно записали 5000 тестов, выходим")
                        exit(0)

                elif line.startswith("DATA_ERROR;"):
                    print("[!] Пропуск итерации: тайм-аут сигнала на стороне Arduino.")

except KeyboardInterrupt:
    print(f"\nСбор данных завершен. Всего тестов обработано: {total_count}. Файл сохранен.")
except PermissionError:
    print(f"\nОшибка прав доступа. Забыли сделать 'sudo chmod 666 {SERIAL_PORT}'?")
except Exception as e:
    print(f"\nКритическая ошибка: {e}")
