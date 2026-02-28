from basic_operations import unsigned_to_decimal, clean_zeros, is_greater_or_equal, subtract_binary
from typing import List
from consts import NUMB_OF_BITS, LEN_OF_MANTISS, EXP_CONST, END_OF_EXP


def float_to_ieee_bin(f: float) -> List[int]:
    """Ручной перевод десятичной дроби в 32-битный массив IEEE-754."""
    if f == 0.0:
        return [0] * NUMB_OF_BITS

    sign = 1 if f < 0 else 0
    f = abs(f)
    int_part = int(f)
    frac_part = f - int_part

    int_bits = []
    while int_part > 0:
        int_bits.insert(0, int_part % 2)
        int_part //= 2

    frac_bits = []
    while frac_part > 0 and len(frac_bits) < 40:
        frac_part *= 2
        if frac_part >= 1:
            frac_bits.append(1)
            frac_part -= 1
        else:
            frac_bits.append(0)

    if int_bits:
        exp = len(int_bits) - 1
        mantissa = int_bits[1:] + frac_bits
    else:
        try:
            first_one = frac_bits.index(1)
        except ValueError:
            return [sign] + [0] * (NUMB_OF_BITS-1)
        exp = -(first_one + 1)
        mantissa = frac_bits[first_one + 1:]

    exp_biased = exp + EXP_CONST
    exp_bits = []
    for _ in range(8):
        exp_bits.insert(0, exp_biased % 2)
        exp_biased //= 2

    mantissa = mantissa[:LEN_OF_MANTISS]
    while len(mantissa) < LEN_OF_MANTISS:
        mantissa.append(0)

    return [sign] + exp_bits + mantissa

def ieee_bin_to_float(bits: List[int]) -> float:
    """Ручной перевод 32-битного массива IEEE-754 обратно в float."""
    if all(b == 0 for b in bits[1:]):
        return 0.0

    sign = -1 if bits[0] == 1 else 1
    exp_val = unsigned_to_decimal(bits[1:END_OF_EXP])

    mantissa_val = 1.0
    for i, b in enumerate(bits[END_OF_EXP:NUMB_OF_BITS]):
        if b == 1:
            mantissa_val += 2 ** -(i + 1)

    return sign * mantissa_val * (2 ** (exp_val - EXP_CONST))

def add_mantissas(a: List[int], b: List[int]) -> List[int]:
    """Складывает два бинарных массива одинаковой длины. Может вернуть массив на 1 бит длиннее (перенос)."""
    res = []
    carry = 0
    for i in range(len(a) - 1, -1, -1):
        total = a[i] + b[i] + carry
        res.insert(0, total % 2)
        carry = total // 2
    if carry:
        res.insert(0, 1)
    return res

def is_greater_or_equal_fixed(a: List[int], b: List[int]) -> bool:
    """Сравнивает два массива одинаковой длины побитово (без удаления нулей)."""
    for bit_a, bit_b in zip(a, b):
        if bit_a > bit_b: return True
        if bit_a < bit_b: return False
    return True

def subtract_mantissas(a: List[int], b: List[int]) -> List[int]:
    """Вычитает b из a (a >= b). Строго сохраняет длину массива (ведущие нули остаются)."""
    res = []
    borrow = 0
    for i in range(len(a) - 1, -1, -1):
        diff = a[i] - b[i] - borrow
        if diff < 0:
            diff += 2
            borrow = 1
        else:
            borrow = 0
        res.insert(0, diff)
    return res

def decimal_to_binary_8bit(val: int) -> List[int]:
    """Переводит целое число в строго 8-битный массив (для экспоненты)."""
    arr = [0] * 8
    for i in range(7, -1, -1):
        arr[i] = val % 2
        val //= 2
    return arr

def add_ieee(x1: List[int], x2: List[int]) -> List[int]:
    sign1 = x1[0]
    sign2 = x2[0]

    exp1 = unsigned_to_decimal(x1[1:END_OF_EXP])
    exp2 = unsigned_to_decimal(x2[1:END_OF_EXP])
    final_exp = max(exp1, exp2)

    man1 = [1] + x1[END_OF_EXP:NUMB_OF_BITS]
    man2 = [1] + x2[END_OF_EXP:NUMB_OF_BITS]

    if exp1 < exp2:
        diff = exp2 - exp1
        man1 = ([0] * diff) + man1
        man2 = man2 + ([0] * diff)
    elif exp1 > exp2:
        diff = exp1 - exp2
        man2 = ([0] * diff) + man2
        man1 = man1 + ([0] * diff)

    if sign1 == sign2:
        final_sign = sign1
        sum_man = add_mantissas(man1, man2)

        if len(sum_man) > len(man1):
            final_exp += 1
            sum_man.pop()

    else:
        if is_greater_or_equal_fixed(man1, man2):
            final_sign = sign1
            sum_man = subtract_mantissas(man1, man2)
        else:
            final_sign = sign2
            sum_man = subtract_mantissas(man2, man1)

        if sum_man == [0] * len(sum_man):
            return [0] * NUMB_OF_BITS

        while sum_man[0] == 0:
            sum_man.pop(0)
            sum_man.append(0)
            final_exp -= 1

    final_man = sum_man[1:LEN_OF_MANTISS+1]

    while len(final_man) < LEN_OF_MANTISS:
        final_man.append(0)

    final_exp_bits = decimal_to_binary_8bit(final_exp)

    ans = [final_sign] + final_exp_bits + final_man
    return ans

def multiply_mantissas(a: List[int], b: List[int]) -> List[int]:
    """Умножает два бинарных массива. Возвращает массив длиной len(a) + len(b)."""
    res = [0] * (len(a) + len(b))
    for i in range(len(b) - 1, -1, -1):
        if b[i] == 1:
            carry = 0
            offset = len(b) - 1 - i
            for j in range(len(a) - 1, -1, -1):
                pos = len(res) - 1 - offset - (len(a) - 1 - j)
                total = res[pos] + a[j] + carry
                res[pos] = total % 2
                carry = total // 2
            if carry:
                res[len(res) - 1 - offset - len(a)] += carry
    return res

def multiply_ieee(x1: List[int], x2: List[int]) -> List[int]:
    sign = x1[0] ^ x2[0]

    if all(b == 0 for b in x1[1:NUMB_OF_BITS]) or all(b == 0 for b in x2[1:NUMB_OF_BITS]):
        return [sign] + [0]*(NUMB_OF_BITS-1)

    exp1 = unsigned_to_decimal(x1[1:END_OF_EXP])
    exp2 = unsigned_to_decimal(x2[1:END_OF_EXP])
    final_exp = exp1 + exp2 - EXP_CONST

    man1 = [1] + x1[END_OF_EXP:NUMB_OF_BITS]
    man2 = [1] + x2[END_OF_EXP:NUMB_OF_BITS]

    prod = multiply_mantissas(man1, man2)

    if prod[0] == 1:
        final_exp += 1
        final_man = prod[1:LEN_OF_MANTISS+1]
    else:
        final_man = prod[2:LEN_OF_MANTISS+2]

    final_exp_bits = decimal_to_binary_8bit(final_exp)
    return [sign] + final_exp_bits + final_man

def divide_ieee(x1: List[int], x2: List[int]) -> List[int]:
    if all(b == 0 for b in x2[1:NUMB_OF_BITS]):
        raise ZeroDivisionError("Cannot divide by zero in IEEE-754")

    if all(b == 0 for b in x1[1:NUMB_OF_BITS]):
        return [x1[0] ^ x2[0]] + [0] * (NUMB_OF_BITS-1)

    sign = x1[0] ^ x2[0]

    exp1 = unsigned_to_decimal(x1[1:END_OF_EXP])
    exp2 = unsigned_to_decimal(x2[1:END_OF_EXP])
    final_exp = exp1 - exp2 + EXP_CONST

    man1 = [1] + x1[END_OF_EXP:NUMB_OF_BITS]
    man2 = [1] + x2[END_OF_EXP:NUMB_OF_BITS]
    man2_clean = clean_zeros(man2)

    int_part = []
    cur = []
    for bit in man1:
        cur.append(bit)
        cur = clean_zeros(cur)
        if is_greater_or_equal(cur, man2_clean):
            int_part.append(1)
            cur = subtract_binary(cur, man2_clean)
        else:
            if len(int_part) > 0:
                int_part.append(0)
    if not int_part:
        int_part = [0]

    frac_part = []
    for _ in range(25):
        cur.append(0)
        cur = clean_zeros(cur)
        if is_greater_or_equal(cur, man2_clean):
            frac_part.append(1)
            cur = subtract_binary(cur, man2_clean)
        else:
            frac_part.append(0)

    full_res = int_part + frac_part

    try:
        first_one_idx = full_res.index(1)
    except ValueError:
        return [0] * NUMB_OF_BITS

    final_exp -= first_one_idx

    start_idx = first_one_idx + 1
    final_man = full_res[start_idx: start_idx + LEN_OF_MANTISS]

    while len(final_man) < LEN_OF_MANTISS:
        final_man.append(0)

    final_exp_bits = decimal_to_binary_8bit(final_exp)
    return [sign] + final_exp_bits + final_man