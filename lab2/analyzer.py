from config import *


def get_zhegalkin_coeffs(table: list) -> list:
    """
    Вычисляет коэффициенты полинома Жегалкина методом треугольника (треугольник Паскаля).
    """
    current_layer = [res for _, res in table]
    coeffs = [current_layer[0]]
    for _ in range(len(current_layer) - 1):
        next_layer = get_next_layer(current_layer)
        coeffs.append(next_layer[0])
        current_layer = next_layer
    return coeffs


def get_next_layer(layer: list) -> list:
    """
    Формирует следующий слой для вычисления коэффициентов Жегалкина путем XOR соседних элементов.
    """
    next_layer = []
    for i in range(len(layer) - 1):
        next_layer.append(layer[i] ^ layer[i + 1])
    return next_layer


def build_zhegalkin_poly(coeffs: list, variables: list) -> str:
    """
    Собирает строковое представление полинома Жегалкина.
    """
    terms = []
    num_vars = len(variables)
    for i, coeff in enumerate(coeffs):
        if coeff == VAL_TRUE:
            binary_str = bin(i)[2:].zfill(num_vars)
            term_vars = [variables[j] for j in range(num_vars) if binary_str[j] == '1']
            terms.append("".join(term_vars) if term_vars else "1")
    return " ⊕ ".join(terms) if terms else "0"


def calc_derivative_vector(vector: list, var_idx: int, num_vars: int) -> list:
    """Считает производную по одной переменной для вектора значений."""
    deriv = []
    bit_pos = num_vars - 1 - var_idx
    lower_mask = (1 << bit_pos) - 1
    for i in range(len(vector) // 2):
        idx0 = ((i >> bit_pos) << (bit_pos + 1)) | (i & lower_mask)
        idx1 = idx0 | (1 << bit_pos)
        deriv.append(vector[idx0] ^ vector[idx1])
    return deriv


def get_mixed_derivative(table: list, target_vars: list, variables: list) -> list:
    """Вычисляет частную (1 переменная) или смешанную (>1) производную. Размерность уменьшается."""
    current_vector = [res for _, res in table]
    current_vars = variables[:]

    for var in target_vars:
        if var not in current_vars:
            continue
        var_idx = current_vars.index(var)
        num_vars = len(current_vars)
        current_vector = calc_derivative_vector(current_vector, var_idx, num_vars)
        current_vars.pop(var_idx)
    return current_vector


def find_fictitious_vars(table: list, variables: list) -> list:
    """Находит фиктивные переменные (если первая производная равна нулю)."""
    fictitious = []
    for var in variables:
        deriv = get_mixed_derivative(table, [var], variables)
        if all(val == 0 for val in deriv):
            fictitious.append(var)
    return fictitious