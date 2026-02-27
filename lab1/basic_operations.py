from typing import List, Tuple

def decimal_to_binary(x: int) -> List[int]:
    """Переводит десятичное число в 32-битный массив (прямой код: знак + модуль)."""
    arr = [0] * 32
    if x < 0:
        arr[0] = 1

    x = abs(x)
    i = 31

    while x != 0 and i > 0:
        arr[i] = x % 2
        x //= 2
        i -= 1

    return arr

def from_binary_to_decimal(bits: List[int]) -> int:
    """Переводит 32-битный массив (прямой код) обратно в десятичное число."""
    ans = 0
    for bit in bits[1:]:
        ans = ans * 2 + bit

    if bits[0] == 1:
        ans *= -1

    return ans

def unsigned_to_decimal(bits: List[int]) -> int:
    """Переводит беззнаковый массив битов в число (используется для экспоненты IEEE-754)."""
    ans = 0
    for bit in bits:
        ans = ans * 2 + bit
    return ans

def decimal_to_ones_complement(x: int) -> List[int]:
    """Переводит в обратный код (для отрицательных инвертируем все биты модуля)."""
    arr = decimal_to_binary(x)
    if arr[0] == 1:
        for i in range(1, 32):
            arr[i] = 1 - arr[i]
    return arr

def twos_complement(arr: List[int]) -> List[int]:
    """Универсальная функция перевода из прямого кода в дополнительный и обратно."""
    if arr[0] == 0:
        return arr.copy()

    res = arr.copy()
    for i in range(1, 32):
        res[i] = 1 - res[i]

    for i in range(31, 0, -1):
        res[i] += 1
        if res[i] == 2:
            res[i] = 0
        else:
            break

    return res

def add_binary(x1: int, x2: int) -> List[int]:
    """Складывает два десятичных числа, используя бинарную арифметику (дополнительный код).
       Возвращает результат в прямом коде."""
    bin1 = twos_complement(decimal_to_binary(x1))
    bin2 = twos_complement(decimal_to_binary(x2))

    ans = [0] * 32
    carry = 0

    for bit in range(31, -1, -1):
        total = bin1[bit] + bin2[bit] + carry
        ans[bit] = total % 2
        carry = total // 2

    return twos_complement(ans)

def minus_binary(x1: int, x2: int) -> List[int]:
    """Вычитает x2 из x1 (эквивалентно x1 + (-x2))."""
    return add_binary(x1, -x2)

def multiply(x1: int, x2: int) -> List[int]:
    """Умножает два числа в бинарном виде (прямой код)."""
    if x1 == 0 or x2 == 0:
        return [0] * 32

    bin1 = decimal_to_binary(x1)
    bin2 = decimal_to_binary(x2)

    ans = [0] * 32
    ans[0] = bin1[0] ^ bin2[0]

    for i in range(31, 0, -1):
        if bin2[i] == 1:
            diff = 31 - i
            for j in range(31, 0, -1):
                if j - diff > 0:
                    ans[j - diff] += bin1[j]

    for i in range(31, 0, -1):
        carry = ans[i] // 2
        ans[i] %= 2
        if i > 1:
            ans[i - 1] += carry

    return ans

def clean_zeros(bin_array: List[int]) -> List[int]:
    """Удаляет ведущие нули из бинарного массива (для деления и сравнения)."""
    res = list(bin_array)
    while len(res) > 1 and res[0] == 0:
        res.pop(0)
    return res

def is_greater_or_equal(a: List[int], b: List[int]) -> bool:
    """Сравнивает два бинарных числа (без знака). Возвращает True, если a >= b."""
    a, b = clean_zeros(a), clean_zeros(b)

    if len(a) > len(b): return True
    if len(a) < len(b): return False

    for bit_a, bit_b in zip(a, b):
        if bit_a > bit_b: return True
        if bit_a < bit_b: return False

    return True

def subtract_binary(a: List[int], b: List[int]) -> List[int]:
    """Вычитает массив b из a (используется только для модулей при делении). Предполагается a >= b."""
    a, b = clean_zeros(a), clean_zeros(b)
    b = [0] * (len(a) - len(b)) + b

    result = []
    borrow = 0

    for i in range(len(a) - 1, -1, -1):
        diff = a[i] - b[i] - borrow
        if diff < 0:
            diff += 2
            borrow = 1
        else:
            borrow = 0
        result.insert(0, diff)

    return clean_zeros(result)

def divide(x1: int, x2: int) -> Tuple[int, List[int], List[int]]:
    """Делит x1 на x2."""
    if x2 == 0:
        raise ZeroDivisionError("Cannot divide by zero")

    x1_bin = decimal_to_binary(x1)
    x2_bin = decimal_to_binary(x2)

    sign = x1_bin[0] ^ x2_bin[0]

    x1_mag = clean_zeros(x1_bin[1:])
    x2_mag = clean_zeros(x2_bin[1:])

    integer = []
    float_arr = []
    cur = []

    for bit in x1_mag:
        cur.append(bit)
        cur = clean_zeros(cur)

        if is_greater_or_equal(cur, x2_mag):
            integer.append(1)
            cur = subtract_binary(cur, x2_mag)
        else:
            if len(integer) > 0:
                integer.append(0)

    if not integer:
        integer = [0]

    precision_bits = 17
    for _ in range(precision_bits):
        if len(cur) == 1 and cur[0] == 0:
            float_arr.append(0)
            continue

        cur.append(0)
        cur = clean_zeros(cur)

        if is_greater_or_equal(cur, x2_mag):
            float_arr.append(1)
            cur = subtract_binary(cur, x2_mag)
        else:
            float_arr.append(0)

    return sign, integer, float_arr