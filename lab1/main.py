from basic_operations import (
    decimal_to_binary, decimal_to_ones_complement, from_binary_to_decimal,
    twos_complement, add_binary, minus_binary, multiply, divide
)
from ieee import (
    add_ieee, multiply_ieee, divide_ieee,
    float_to_ieee_bin, ieee_bin_to_float
)
from bcd_2421 import (
    add_2421_numbers, int_to_2421_array, array_2421_to_int
)
from typing import List

def print_bin(arr: List[int]) -> str:
    """Вспомогательная функция для красивого вывода массива."""
    return "".join(map(str, arr))

def main():
    while True:
        print("\n" + "=" * 50)
        print(" ОПЕРАЦИИ ")
        print("=" * 50)
        print("1. Перевод в прямой, обратный и дополнительный коды")
        print("2. Сложение 2 чисел в дополнительном коде")
        print("3. Вычитание 2 чисел в дополнительном коде")
        print("4. Умножение 2 чисел в прямом коде")
        print("5. Деление 2 чисел в прямом коде (до 5 знаков)")
        print("6. Операции с плавающей точкой (IEEE-754)")
        print("7. Сложение в коде 2421 BCD")
        print("0. Выход")
        print("-" * 50)

        choice = input("Выберите пункт меню: ")

        if choice == '0':
            print("Завершение работы.")
            break

        elif choice == '1':
            num = int(input("Введите десятичное число: "))
            print(f"Прямой код:         {print_bin(decimal_to_binary(num))}")
            print(f"Обратный код:       {print_bin(decimal_to_ones_complement(num))}")
            print(f"Дополнительный код: {print_bin(twos_complement(decimal_to_binary(num)))}")

        elif choice == '2':
            x1 = int(input("Первое число: "))
            x2 = int(input("Второе число: "))
            res_bin = add_binary(x1, x2)
            res_dec = from_binary_to_decimal(res_bin)
            print(f"Результат (2-ый):  {print_bin(res_bin)}")
            print(f"Результат (10-ый): {res_dec}")

        elif choice == '3':
            x1 = int(input("Уменьшаемое: "))
            x2 = int(input("Вычитаемое: "))
            res_bin = minus_binary(x1, x2)
            res_dec = from_binary_to_decimal(res_bin)
            print(f"Результат (2-ый):  {print_bin(res_bin)}")
            print(f"Результат (10-ый): {res_dec}")

        elif choice == '4':
            x1 = int(input("Первое число: "))
            x2 = int(input("Второе число: "))
            res_bin = multiply(x1, x2)
            res_dec = from_binary_to_decimal(res_bin)
            print(f"Результат (2-ый):  {print_bin(res_bin)}")
            print(f"Результат (10-ый): {res_dec}")

        elif choice == '5':
            x1 = int(input("Делимое: "))
            x2 = int(input("Делитель: "))
            try:
                sign, int_part, float_part = divide(x1, x2)
                bin_str = ("-" if sign else "") + print_bin(int_part) + "." + print_bin(float_part)

                int_val = 0
                for b in int_part: int_val = int_val * 2 + b
                float_val = 0
                for i, b in enumerate(float_part): float_val += b * (2 ** -(i + 1))
                dec_val = (-1 if sign else 1) * (int_val + float_val)

                print(f"Результат (2-ый):  {bin_str}")
                print(f"Результат (10-ый): {dec_val:.5f}")
            except ZeroDivisionError:
                print("Ошибка: Деление на ноль!")

        elif choice == '6':
            f1 = float(input("Первое число (float): "))
            f2 = float(input("Второе число (float): "))
            op = input("Выберите операцию (+, -, *, /): ")

            bin1 = float_to_ieee_bin(f1)
            bin2 = float_to_ieee_bin(f2)

            res_bin = []
            if op == '+':
                res_bin = add_ieee(bin1, bin2)
            elif op == '-':
                bin2_neg = bin2.copy()
                bin2_neg[0] = 1 - bin2_neg[0]
                res_bin = add_ieee(bin1, bin2_neg)
            elif op == '*':
                res_bin = multiply_ieee(bin1, bin2)
            elif op == '/':
                try:
                    res_bin = divide_ieee(bin1, bin2)
                except ZeroDivisionError:
                    print("Ошибка: Деление на ноль!")
                    continue
            else:
                print("Неизвестная операция.")
                continue

            res_dec = ieee_bin_to_float(res_bin)
            print(f"IEEE-754 (2-ый):   {print_bin(res_bin)}")
            print(f"Результат (10-ый): {res_dec}")

        elif choice == '7':
            x1 = int(input("Первое положительное число: "))
            x2 = int(input("Второе положительное число: "))

            arr1 = int_to_2421_array(x1)
            arr2 = int_to_2421_array(x2)

            res_arr = add_2421_numbers(arr1, arr2)
            res_dec = array_2421_to_int(res_arr)

            bin_str = " ".join(["".join(map(str, tetrad)) for tetrad in res_arr])
            print(f"Результат (2-ый 2421): {bin_str}")
            print(f"Результат (10-ый):     {res_dec}")

        else:
            print("Неверный ввод. Пожалуйста, выберите число от 0 до 7.")

if __name__ == "__main__":
    main()