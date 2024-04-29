# Подключение библиотек
import argparse
from remove_dublication import RemoveDuplicatesSign
from merge_file import MergeFile
from visualization import visualization
from load_data import LoadFile
from receive_sign import ReceiveSign
from save_file import save_file
import time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--file_in_1', type=str, help='Input file path for car data')
    parser.add_argument('--file_in_2', type=str, help='Input file path for sign data')
    parser.add_argument('--file_out', type=str, help='Input file path for sign data')
    args = parser.parse_args()

    if args.file_in_1 and args.file_in_2 and args.file_out:
        file_1 = args.file_in_1
        file_2 = args.file_in_2
        file_3 = args.file_out
    else:
        print("Please provide both input and output file paths using --file_in and --file_out options.")
        exit()

    start = time.time()

    car_data = LoadFile(file_1)
    ai_data = LoadFile(file_2)
    merge_data = MergeFile(car_data, ai_data)
    sign = ReceiveSign()
    sign.calculation_sign(merge_data)
    unique_sign = RemoveDuplicatesSign()
    to_file = unique_sign.merge_similar_signs(sign.get_data())
    save_file(file_3, to_file)

    visualization(sign)
    end = time.time()

    print('TIME: ', end - start)

# python new_script.py --file_in_1 digest.csv --file_in_2 20230520-203319_predictions.csv --file_out test_final.csv