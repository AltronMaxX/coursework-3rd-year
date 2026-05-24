import os
import pandas as pd

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
    

    print(f"Успешно загружено тестов: {len(vals)}")
    print("=" * 60)


    if len(vals) > 0:
        print(f"Минимальная длительность сигнала: {vals.min():.4f} мкс")
        print(f"Средняя длительность сигналов:     {vals.mean():.4f} мкс")
        print(f"Максимальная длительность сигнала: {vals.max():.4f} мкс")

    print("=" * 60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_file(sys.argv[1])
