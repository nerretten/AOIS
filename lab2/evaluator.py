from config import *


def evaluate_operator(op: str, val1: int, val2: int = None) -> int:
    """
    Вычисляет результат применения логического оператора к операндам.

    Args:
        op (str): Строковое представление оператора.
        val1 (int): Первый операнд (0 или 1).
        val2 (int, optional): Второй операнд (0 или 1). Для унарных операций не нужен.

    Returns:
        int: Результат логической операции (0 или 1).
    """
    if op == OP_NOT:
        return VAL_FALSE if val1 == VAL_TRUE else VAL_TRUE
    if op == OP_AND:
        return val1 & val2
    if op == OP_OR:
        return val1 | val2
    if op == REP_IMP:
        return VAL_FALSE if (val1 == VAL_TRUE and val2 == VAL_FALSE) else VAL_TRUE
    if op == OP_EQ:
        return VAL_TRUE if val1 == val2 else VAL_FALSE
    return VAL_FALSE


def evaluate_rpn(rpn_expr: list, context: dict) -> int:
    """
    Вычисляет значение функции, представленной в RPN, для заданного набора переменных.

    Args:
        rpn_expr (list): Выражение в формате RPN.
        context (dict): Словарь со значениями переменных {имя_переменной: значение}.

    Returns:
        int: Итоговое значение функции (0 или 1).
    """
    stack = []
    for token in rpn_expr:
        if token in context:
            stack.append(context[token])
        elif token == OP_NOT:
            val = stack.pop()
            stack.append(evaluate_operator(token, val))
        else:
            val2 = stack.pop()
            val1 = stack.pop()
            stack.append(evaluate_operator(token, val1, val2))
    return stack[0]


def build_truth_table(rpn_expr: list, variables: list) -> list:
    """
    Строит таблицу истинности для заданной логической функции.

    Args:
        rpn_expr (list): Функция в формате обратной польской записи.
        variables (list): Отсортированный список переменных функции.

    Returns:
        list: Список кортежей вида (контекст_переменных, результат_функции).
    """
    table = []
    num_vars = len(variables)
    total_rows = 2 ** num_vars

    for i in range(total_rows):
        binary_str = bin(i)[2:].zfill(num_vars)
        context = {variables[j]: int(binary_str[j]) for j in range(num_vars)}
        result = evaluate_rpn(rpn_expr, context)
        table.append((context, result))

    return table


def print_truth_table(table: list, variables: list) -> None:
    """
    Форматированно выводит таблицу истинности в консоль.

    Args:
        table (list): Таблица истинности из build_truth_table.
        variables (list): Список переменных для заголовка.
    """
    header = "\t".join(variables) + "\t| F"
    print(header)
    print("-" * len(header) * 2)
    for row in table:
        context, result = row
        values = "\t".join(str(context[var]) for var in variables)
        print(f"{values}\t| {result}")