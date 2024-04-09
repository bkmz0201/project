#!/bin/bash
python -m venv
pip install pandas
pip install geopy
pip install folium
# Проверка, существует ли Python скрипт
python_script="review_4.py"
if [ ! -f "$python_script" ]; then
    echo "Ошибка: Python скрипт '$python_script' не найден."
    exit 1
fi

# Запуск Python скрипта с передачей аргументов
python_output=$(python review_4.py --file_in_1 digest.csv --file_in_2 20230520-203319_predictions.csv --file_out test_final.csv)

# Проверка успешности выполнения Python скрипта
if [ $? -ne 0 ]; then
    echo "Ошибка: Python скрипт завершился с ошибкой."
    exit 1
fi

# Создание временной директории
temp_dir=$(mktemp -d)
archive_name="script_results.tar.gz"

# Проверка успешности создания временной директории
if [ ! -d "$temp_dir" ]; then
    echo "Ошибка: Не удалось создать временную директорию."
    exit 1
fi

# Копирование результата, Python скрипта и Bash во временную директорию
cp "$python_script" "$temp_dir"
cp "$0" "$temp_dir"
echo "$python_output" > "$temp_dir/python_output.txt"

# Ожидание, пока файл test_final.csv не появится
while [ ! -f "test_final.csv" ]; do
    sleep 1
done

# Копирование файла test_final.csv во временную директорию
cp "test_final.csv" "$temp_dir"
while [ ! -f "test_final.html" }; do
	sleep 1
done

cp "test_final.html" "$temp_dir"
# Упаковка временной директории в архив
tar -czvf "$archive_name" -C "$temp_dir" .

# Проверка успешности создания архива
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось создать архив."
    exit 1
fi

# Удаление временной директории
rm -rf "$temp_dir"

echo "Результаты и скрипты упакованы в архив: $archive_name"

