from config import *


def get_zhegalkin_coeffs(table: list) -> list:
    """
    Вычисляет коэффициенты полинома Жегалкина методом треугольника (треугольник Паскаля).

    Args:
        table (list): Таблица истинности.

    Returns:
        list: Список коэффициентов полинома Жегалкина.
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

    Args:
        layer (list): Текущий слой значений.

    Returns:
        list: Следующий слой значений.
    """
    next_layer = []
    for i in range(len(layer) - 1):
        next_layer.append(layer[i] ^ layer[i + 1])
    return next_layer


def build_zhegalkin_poly(coeffs: list, variables: list) -> str:
    """
    Собирает строковое представление полинома Жегалкина.

    Args:
        coeffs (list): Коэффициенты полинома.
        variables (list): Список переменных.

    Returns:
        str: Строка с полиномом Жегалкина.
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
    """Считает производную по одной переменной для вектора значений """
    deriv = []
    for i in range(len(vector)):
        # Создаем маску, где 1 стоит на месте нашей переменной, и делаем XOR индекса
        mask = 1 << (num_vars - 1 - var_idx)
        pair_idx = i ^ mask
        deriv.append(vector[i] ^ vector[pair_idx])
    return deriv


def get_mixed_derivative(table: list, target_vars: list, variables: list) -> list:
    """Вычисляет частную (1 переменная) или смешанную (>1) производную."""
    num_vars = len(variables)
    current_vector = [res for _, res in table]

    for var in target_vars:
        var_idx = variables.index(var)
        current_vector = calc_derivative_vector(current_vector, var_idx, num_vars)
    return current_vector


def find_fictitious_vars(table: list, variables: list) -> list:
    """Находит фиктивные переменные (если первая производная равна нулю)."""
    fictitious = []
    for var in variables:
        deriv = get_mixed_derivative(table, [var], variables)
        if all(val == 0 for val in deriv):
            fictitious.append(var)
    return fictitious