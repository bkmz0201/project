#!/bin/bash
# Активация виртуального окружения для linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	python3 -m venv .venv
	source .venv/bin/activate
fi
if [[ "$OSTYPE" == "darwin"* ]]; then
	python3 -m venv .venv
	source .venv/bin/activate
fi
if [[ "$OSTYPE" == "msys" ]]; then
	python -m venv .venv
	cd .venv/Scripts
	. activate
	cd -
fi
# Установка пакетов в виртуальное окружен
pip install -r requirements.txt
# Проверка, существует ли Python скрипт
python_script="review_4.py"
if [ ! -f "$python_script" ]; then
    echo "Ошибка: Python скрипт '$python_script' не найден."
    exit 1
fi
read -p "Введите путь к первому входному файлу: " file_in_1
read -p "Введите путь ко второму входному файлу: " file_in_2
# Запуск Python скрипта с передачей аргументов
python_output=$(python script.py --file_in_1 "$file_in_1" --file_in_2 "$file_in_2" --file_out test_final.csv)

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

# Создание подкаталога для результатов
results_dir="$temp_dir/results"

program_dir="$temp_dir/program"
mkdir "$results_dir" "$program_dir"


# Копирование результата, Python скрипта и Bash в подкаталог
cp "$python_script" "$program_dir"
echo "$python_output" > "$results_dir/python_output.txt"
cp "test_final.csv" "$results_dir"
cp "test_final.html" "$results_dir"
cp "requirements.txt" "$program_dir"
cp "start.sh" "$program_dir"

# Упаковка подкаталога с результатами в архив
tar -czvf "$archive_name" -C "$temp_dir" results/ program/
# Проверка успешности создания архива
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось создать архив."
    exit 1
fi

# Удаление временной директории
rm -rf "$temp_dir"

deactivate
