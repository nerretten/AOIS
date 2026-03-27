from config import *


def get_sdnf(table: list, variables: list) -> str:
    """
    Строит Совершенную Дизъюнктивную Нормальную Форму (СДНФ) на основе таблицы истинности.

    Args:
        table (list): Таблица истинности.
        variables (list): Список переменных.

    Returns:
        str: Строка, представляющая СДНФ.
    """
    implicants = []
    for context, result in table:
        if result == VAL_TRUE:
            term = get_term_string(context, variables, is_dnf=True)
            implicants.append(f"({term})")
    return " v ".join(implicants) if implicants else "0"


def get_sknf(table: list, variables: list) -> str:
    """
    Строит Совершенную Конъюнктивную Нормальную Форму (СКНФ) на основе таблицы истинности.

    Args:
        table (list): Таблица истинности.
        variables (list): Список переменных.

    Returns:
        str: Строка, представляющая СКНФ.
    """
    implicants = []
    for context, result in table:
        if result == VAL_FALSE:
            term = get_term_string(context, variables, is_dnf=False)
            implicants.append(f"({term})")
    return " & ".join(implicants) if implicants else "1"


def get_term_string(context: dict, variables: list, is_dnf: bool) -> str:
    """
    Формирует строку для отдельного терма (конституенты единицы или нуля).

    Args:
        context (dict): Набор значений переменных.
        variables (list): Список переменных.
        is_dnf (bool): Флаг сборки терма для ДНФ (True) или КНФ (False).

    Returns:
        str: Строковое представление терма.
    """
    parts = []
    for var in variables:
        val = context[var]
        if is_dnf:
            parts.append(var if val == VAL_TRUE else f"¬{var}")
        else:
            parts.append(var if val == VAL_FALSE else f"¬{var}")
    join_str = " & " if is_dnf else " v "
    return join_str.join(parts)


def get_numeric_forms(table: list) -> tuple:
    """
    Получает числовые формы для СДНФ и СКНФ (индексы строк с 1 и 0).

    Args:
        table (list): Таблица истинности.

    Returns:
        tuple: (список индексов для СДНФ, список индексов для СКНФ).
    """
    ones = [i for i, (_, res) in enumerate(table) if res == VAL_TRUE]
    zeros = [i for i, (_, res) in enumerate(table) if res == VAL_FALSE]
    return ones, zeros


def get_index_form(table: list) -> int:
    """
    Вычисляет индексную форму функции.

    Args:
        table (list): Таблица истинности.

    Returns:
        int: Десятичное значение, соответствующее вектору значений функции.
    """
    binary_str = "".join(str(res) for _, res in table)
    return int(binary_str, 2)


def check_post_classes(table: list, coeffs: list) -> dict:
    """
    Проверяет принадлежность функции к основным классам Поста.

    Args:
        table (list): Таблица истинности.
        coeffs (list): Коэффициенты полинома Жегалкина
    Returns:
        dict: Словарь с флагами принадлежности к классам T0, T1, S (самодвойственность) и M (монотонность).
    """
    results_column = [res for _, res in table]
    t0 = results_column[0] == 0
    t1 = results_column[-1] == 1
    self_dual = check_self_dual(results_column)
    monotonic = check_monotonic(table)
    linarity = check_linearity(coeffs)
    return {"T0": t0, "T1": t1, "S": self_dual, "M": monotonic, "L": linarity}


def check_self_dual(results: list) -> bool:
    """
    Проверяет, является ли функция самодвойственной (класс S).

    Args:
        results (list): Вектор значений функции.

    Returns:
        bool: True, если функция самодвойственна.
    """
    length = len(results)
    for i in range(length // 2):
        if results[i] == results[length - 1 - i]:
            return False
    return True


def check_monotonic(table: list) -> bool:
    """
    Проверяет, является ли функция монотонной (класс M).

    Args:
        table (list): Таблица истинности.

    Returns:
        bool: True, если функция монотонна.
    """
    for i in range(len(table)):
        for j in range(i + 1, len(table)):
            if is_preceding(table[i][0], table[j][0]) and table[i][1] > table[j][1]:
                return False
    return True


def check_linearity(coeffs: list) -> bool:
    """
    Проверяет функцию на линейность (класс Поста L) по коэффициентам полинома Жегалкина.

    Args:
        coeffs (list): Коэффициенты полинома.

    Returns:
        bool: True, если функция линейна.
    """
    for i, coeff in enumerate(coeffs):
        if coeff == VAL_TRUE and bin(i).count('1') > 1:
            return False
    return True


def is_preceding(context1: dict, context2: dict) -> bool:
    """
    Проверяет условие предшествования одного набора переменных другому (для монотонности).

    Args:
        context1 (dict): Первый набор значений.
        context2 (dict): Второй набор значений.

    Returns:
        bool: True, если первый набор предшествует второму.
    """
    for var in context1:
        if context1[var] > context2[var]:
            return False
    return True