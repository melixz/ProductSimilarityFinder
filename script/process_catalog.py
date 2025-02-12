#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import argparse
import os
from save_excel import save_excel_with_splitting


def process_catalog(input_file: str, output_file: str) -> None:
    print(f"Загрузка файла: {input_file}")

    # 1. Загрузка данных из Excel
    try:
        df = pd.read_excel(input_file)
        print(f"Файл загружен. Найдено записей: {len(df)}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении файла {input_file}: {e}")

    # Проверка наличия необходимых столбцов
    required_columns = ["Артикул", "Категория", "Название"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"В файле {input_file} отсутствуют обязательные столбцы: {missing_columns}"
        )

    # 2. Объединяем поля "Категория" и "Название", приводим к нижнему регистру
    df["combined"] = (
        df["Категория"].astype(str) + " " + df["Название"].astype(str)
    ).str.lower()
    print("Объединение полей завершено.")

    # 3. Векторизация текста с помощью TF-IDF
    vectorizer = TfidfVectorizer(max_features=50000, min_df=2)
    X = vectorizer.fit_transform(df["combined"])
    print(f"Векторизация завершена. Размерность матрицы признаков: {X.shape}")

    # 4. Поиск похожих товаров (51 сосед, чтобы затем исключить сам товар)
    print("Запуск поиска ближайших соседей...")
    nn = NearestNeighbors(metric="cosine", algorithm="brute", n_jobs=-1)
    nn.fit(X)
    distances, indices = nn.kneighbors(X, n_neighbors=51)
    print("Поиск соседей завершён.")

    # 5. Формирование рекомендаций: для каждого товара выбираем 50 соседей (исключая сам товар)
    recommendations = []
    for i, neighbor_indices in enumerate(indices):
        filtered_neighbors = [idx for idx in neighbor_indices if idx != i]
        for neighbor_idx in filtered_neighbors[:50]:
            recommendations.append(
                {
                    "Артикул": df.iloc[i]["Артикул"],
                    "Связанный артикул": df.iloc[neighbor_idx]["Артикул"],
                }
            )

    recommendations_df = pd.DataFrame(recommendations)
    print(
        f"Формирование рекомендаций завершено. Всего рекомендаций: {len(recommendations_df)}"
    )

    # 6. Сохранение результатов с разбиением на листы
    try:
        save_excel_with_splitting(recommendations_df, output_file)
        print(f"Результаты сохранены в файл: {output_file}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при сохранении файла {output_file}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Нахождение 50 похожих товаров для каждого товара из Excel-файла"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Путь к входному Excel-файлу (например, 'data/Каталог1.xlsx')",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Путь к выходному Excel-файлу (например, 'output/Обработанный_файл1.xlsx')",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Входной файл не найден: {args.input}")

    process_catalog(args.input, args.output)


if __name__ == "__main__":
    main()
