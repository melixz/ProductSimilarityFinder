import pandas as pd
import math


def save_excel_with_splitting(
    df: pd.DataFrame, output_file: str, max_rows: int = 1048576
) -> None:
    """
    Сохраняет DataFrame в Excel, разбивая данные на несколько листов,
    если число строк (с учётом заголовка) превышает max_rows.

    :param df: DataFrame с данными.
    :param output_file: Путь к выходному Excel-файлу.
    :param max_rows: Максимальное число строк на одном листе (по умолчанию 1 048 576).
                     В это число включается строка заголовка.
    """
    total_data_rows = len(df)
    allowed_data_rows = max_rows - 1

    if total_data_rows <= allowed_data_rows:
        df.to_excel(output_file, index=False, engine="openpyxl")
        print(f"Файл сохранён: {output_file}")
    else:
        n_sheets = math.ceil(total_data_rows / allowed_data_rows)
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for i in range(n_sheets):
                start_row = i * allowed_data_rows
                end_row = min(start_row + allowed_data_rows, total_data_rows)
                sheet_df = df.iloc[start_row:end_row]
                sheet_name = f"Sheet{i + 1}"
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                print(f"Лист {sheet_name} сохранён с {len(sheet_df)} строками")
        print(f"Файл {output_file} разбит на {n_sheets} лист(ов).")
