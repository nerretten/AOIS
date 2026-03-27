from config import *


def standardize_expression(expression: str) -> str:
    """
    Очищает выражение от пробелов и заменяет все операторы на односимвольные.
    """
    expr = expression.replace(' ', '')
    expr = expr.replace(OP_OR_ALT, OP_OR)
    expr = expr.replace(OP_IMP, REP_IMP)
    return expr


def validate_expression(expr: str) -> None:
    """
    Проверяет строку на наличие недопустимых символов и склеенных переменных (например, 'aa').
    """
    prev_is_var = False
    valid_chars = ALLOWED_VARS.union({OP_NOT, OP_AND, OP_OR, REP_IMP, OP_EQ, '(', ')'})

    for char in expr:
        if char not in valid_chars:
            raise ValueError(
                f"Ошибка синтаксиса: недопустимый символ '{char}'. Разрешены только {ALLOWED_VARS} и операторы.")

        if char in ALLOWED_VARS:
            if prev_is_var:
                raise ValueError("Ошибка синтаксиса: пропущен оператор между переменными (например, 'aa').")
            prev_is_var = True
        else:
            prev_is_var = False


def is_variable(char: str) -> bool:
    """Проверяет, входит ли символ в список разрешенных переменных."""
    return char in ALLOWED_VARS


def process_operator(char: str, stack: list, output: list) -> None:
    """Обрабатывает логический оператор в соответствии с его приоритетом."""
    current_priority = PRIORITIES.get(char, -1)
    while stack and PRIORITIES.get(stack[-1], -1) >= current_priority:
        output.append(stack.pop())
    stack.append(char)


def handle_brackets(char: str, stack: list, output: list) -> None:
    """Обрабатывает открывающие и закрывающие скобки."""
    if char == '(':
        stack.append(char)
    elif char == ')':
        while stack and stack[-1] != '(':
            output.append(stack.pop())
        if stack:
            stack.pop()


def build_rpn(expression: str) -> list:
    """Преобразует инфиксное выражение в обратную польскую запись с предварительной валидацией."""
    standard_expr = standardize_expression(expression)
    validate_expression(standard_expr)

    output_queue = []
    operator_stack = []

    for char in standard_expr:
        if is_variable(char):
            output_queue.append(char)
        elif char in [OP_NOT, OP_AND, OP_OR, REP_IMP, OP_EQ]:
            process_operator(char, operator_stack, output_queue)
        elif char in ['(', ')']:
            handle_brackets(char, operator_stack, output_queue)

    while operator_stack:
        output_queue.append(operator_stack.pop())
    return output_queue


def extract_variables(rpn_expr: list) -> list:
    """Извлекает уникальные переменные из RPN выражения."""
    variables = set(token for token in rpn_expr if is_variable(token))
    return sorted(list(variables))