from typing import List, Tuple

def int_to_2421_array(num: int) -> List[List[int]]:
    """Переводит число в массив тетрад 2421."""
    dict_2421 = {
        '0': [0, 0, 0, 0], '1': [0, 0, 0, 1], '2': [0, 0, 1, 0], '3': [0, 0, 1, 1], '4': [0, 1, 0, 0],
        '5': [1, 0, 1, 1], '6': [1, 1, 0, 0], '7': [1, 1, 0, 1], '8': [1, 1, 1, 0], '9': [1, 1, 1, 1]
    }
    return [dict_2421[digit] for digit in str(abs(num))]

def array_2421_to_int(arr: List[List[int]]) -> int:
    """Переводит массив тетрад 2421 обратно в число."""
    dict_2421_rev = {
        "0000": '0', "0001": '1', "0010": '2', "0011": '3', "0100": '4',
        "1011": '5', "1100": '6', "1101": '7', "1110": '8', "1111": '9'
    }
    res_str = "".join([dict_2421_rev["".join(map(str, tetrad))] for tetrad in arr])
    return int(res_str)

def add_4bit_binary(a: List[int], b: List[int], cin: int = 0) -> Tuple[int, List[int]]:
    """Вспомогательная функция: обычное 4-битное двоичное сложение."""
    ans = [0] * 4
    carry = cin
    for i in range(3, -1, -1):
        total = a[i] + b[i] + carry
        ans[i] = total % 2
        carry = total // 2
    return carry, ans

def add_2421_digit(digit1: List[int], digit2: List[int], carry_in: int = 0) -> Tuple[int, List[int]]:
    """
    Складывает две цифры (тетрады по 4 бита) в коде 2421 (Aiken).
    Возвращает кортеж: (перенос_в_следующий_разряд, [4_бита_результата]).
    """
    cout, z_bits = add_4bit_binary(digit1, digit2, carry_in)

    z_val = z_bits[0] * 8 + z_bits[1] * 4 + z_bits[2] * 2 + z_bits[3]

    if 5 <= z_val <= 10:
        if cout == 0:
            _, z_bits = add_4bit_binary(z_bits, [0, 1, 1, 0])
        else:
            _, z_bits = add_4bit_binary(z_bits, [1, 0, 1, 0])

    return cout, z_bits

def add_2421_numbers(num1: List[List[int]], num2: List[List[int]]) -> List[List[int]]:
    """Складывает массивы тетрад (многоразрядные числа BCD 2421)."""
    max_len = max(len(num1), len(num2))
    num1 = [[0, 0, 0, 0]] * (max_len - len(num1)) + num1
    num2 = [[0, 0, 0, 0]] * (max_len - len(num2)) + num2

    result = []
    carry = 0

    for i in range(max_len - 1, -1, -1):
        carry, sum_digit = add_2421_digit(num1[i], num2[i], carry)
        result.insert(0, sum_digit)

    if carry == 1:
        result.insert(0, [0, 0, 0, 1])

    return result