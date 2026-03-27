import pytest
from unittest.mock import patch
import io
import itertools

from config import *
from evaluator import evaluate_operator, evaluate_rpn, build_truth_table, print_truth_table
from parser import (standardize_expression, validate_expression, is_variable,
                    process_operator, handle_brackets, build_rpn, extract_variables)
from normal_forms import (get_sdnf, get_sknf, get_term_string, get_numeric_forms,
                          get_index_form, check_post_classes, check_self_dual,
                          check_monotonic, check_linearity, is_preceding)
from analyzer import (get_zhegalkin_coeffs, get_next_layer, build_zhegalkin_poly,
                      calc_derivative_vector, get_mixed_derivative, find_fictitious_vars)
from minimization import (get_binary_implicants, glue_step, get_diff_index, calculate_method,
                          tabular_calc_method, print_karnaugh_map, covers,
                          get_prime_implicants_quiet, get_minimal_cover, format_final_mdnf)
from main import main


# ========================
# ТЕСТЫ ДЛЯ EVALUATOR.PY
# ========================
@pytest.mark.parametrize("op, val1, val2, expected", [
    (OP_NOT, 1, None, 0),
    (OP_NOT, 0, None, 1),
    (OP_AND, 1, 1, 1),
    (OP_AND, 1, 0, 0),
    (OP_OR, 1, 0, 1),
    (OP_OR, 0, 0, 0),
    (REP_IMP, 1, 0, 0),
    (REP_IMP, 0, 1, 1),
    (OP_EQ, 1, 1, 1),
    (OP_EQ, 1, 0, 0),
    ('unknown', 1, 1, 0)  # Фоллбэк
])
def test_evaluate_operator(op, val1, val2, expected):
    assert evaluate_operator(op, val1, val2) == expected


def test_evaluate_rpn():
    rpn = ['a', 'b', '&', 'c', '|']
    context = {'a': 1, 'b': 0, 'c': 1}
    assert evaluate_rpn(rpn, context) == 1

    rpn_not = ['a', '!']
    assert evaluate_rpn(rpn_not, {'a': 1}) == 0


def test_build_and_print_truth_table(capsys):
    rpn = ['a', 'b', '&']
    variables = ['a', 'b']
    table = build_truth_table(rpn, variables)
    assert len(table) == 4
    assert table[0] == ({'a': 0, 'b': 0}, 0)
    assert table[-1] == ({'a': 1, 'b': 1}, 1)

    print_truth_table(table, variables)
    captured = capsys.readouterr()
    assert "a\tb\t| F" in captured.out
    assert "0\t0\t| 0" in captured.out


# ========================
# ТЕСТЫ ДЛЯ PARSER.PY
# ========================
def test_standardize_expression():
    expr = "a v b -> c"
    assert standardize_expression(expr) == "a|b>c"


def test_validate_expression():
    validate_expression("a&b|!c")
    validate_expression("(a>b)~c")

    with pytest.raises(ValueError, match="недопустимый символ"):
        validate_expression("a & b + c")

    with pytest.raises(ValueError, match="пропущен оператор"):
        validate_expression("ab")


def test_build_rpn_and_extract():
    expr = "!(a | b) -> c"
    rpn = build_rpn(expr)
    assert rpn == ['a', 'b', '|', '!', 'c', '>']

    vars_list = extract_variables(rpn)
    assert vars_list == ['a', 'b', 'c']


def test_handle_brackets():
    stack = []
    output = []
    handle_brackets('(', stack, output)
    assert stack == ['(']
    stack.append('&')
    handle_brackets(')', stack, output)
    assert output == ['&']
    assert stack == []


# ========================
# ТЕСТЫ ДЛЯ NORMAL_FORMS.PY
# ========================
@pytest.fixture
def sample_table():
    return [
        ({'a': 0, 'b': 0}, 0),
        ({'a': 0, 'b': 1}, 1),
        ({'a': 1, 'b': 0}, 1),
        ({'a': 1, 'b': 1}, 0)
    ]


def test_sdnf_sknf(sample_table):
    vars_list = ['a', 'b']
    sdnf = get_sdnf(sample_table, vars_list)
    assert sdnf == "(¬a & b) v (a & ¬b)"

    sknf = get_sknf(sample_table, vars_list)
    assert sknf == "(a v b) & (¬a v ¬b)"

    # Краевые случаи: все 0 или все 1
    table_zeros = [({'a': 0}, 0), ({'a': 1}, 0)]
    assert get_sdnf(table_zeros, ['a']) == "0"
    assert get_sknf(table_zeros, ['a']) == "(a) & (¬a)"

    table_ones = [({'a': 0}, 1), ({'a': 1}, 1)]
    assert get_sdnf(table_ones, ['a']) == "(¬a) v (a)"
    assert get_sknf(table_ones, ['a']) == "1"


def test_numeric_and_index_forms(sample_table):
    ones, zeros = get_numeric_forms(sample_table)
    assert ones == [1, 2]
    assert zeros == [0, 3]

    assert get_index_form(sample_table) == int("0110", 2)  # 6


def test_post_classes():
    # Функция XOR: не T0(если 00->0 - T0 выполняется), 00->0, 11->0 (не T1)
    table_xor = [({'a': 0}, 0), ({'a': 1}, 1)]
    coeffs = [0, 1]
    classes = check_post_classes(table_xor, coeffs)
    assert classes["T0"] is True
    assert classes["T1"] is True

    assert check_self_dual([0, 1, 1, 0]) is False
    assert check_self_dual([0, 1, 0, 1]) is True  # самодвойственная

    assert check_monotonic([({'a': 0}, 0), ({'a': 1}, 1)]) is True
    assert check_monotonic([({'a': 0}, 1), ({'a': 1}, 0)]) is False

    assert check_linearity([0, 1, 1, 0]) is True  # a + b (линейна)
    assert check_linearity([0, 0, 0, 1]) is False  # a * b (не линейна)


# ========================
# ТЕСТЫ ДЛЯ ANALYZER.PY
# ========================
def test_zhegalkin():
    table = [({}, 0), ({}, 0), ({}, 0), ({}, 1)]  # конъюнкция
    coeffs = get_zhegalkin_coeffs(table)
    assert coeffs == [0, 0, 0, 1]
    poly = build_zhegalkin_poly(coeffs, ['a', 'b'])
    assert poly == "ab"

    assert build_zhegalkin_poly([0, 0, 0, 0], ['a', 'b']) == "0"
    assert build_zhegalkin_poly([1, 0, 0, 0], ['a', 'b']) == "1"


def test_derivatives_and_fictitious():
    # a | b (0, 1, 1, 1)
    table = [({'a': 0, 'b': 0}, 0), ({'a': 0, 'b': 1}, 1), ({'a': 1, 'b': 0}, 1), ({'a': 1, 'b': 1}, 1)]
    vars_list = ['a', 'b']

    # Производная по a для (a|b) - не ноль
    deriv_a = get_mixed_derivative(table, ['a'], vars_list)
    assert deriv_a != [0, 0, 0, 0]

    # Фиктивная переменная (функция f(a,b) = a)
    table_fict = [({'a': 0, 'b': 0}, 0), ({'a': 0, 'b': 1}, 0), ({'a': 1, 'b': 0}, 1), ({'a': 1, 'b': 1}, 1)]
    assert find_fictitious_vars(table_fict, vars_list) == ['b']


# ========================
# ТЕСТЫ ДЛЯ MINIMIZATION.PY
# ========================
def test_diff_index_and_glue():
    assert get_diff_index("000", "001") == 2
    assert get_diff_index("000", "111") == -1

    implicants = ["000", "001", "111"]
    new_impls, un_glued = glue_step(implicants)
    assert "00X" in new_impls
    assert "111" in un_glued


def test_minimization_methods(capsys):
    table = [
        ({'a': 0, 'b': 0, 'c': 0}, 1),
        ({'a': 0, 'b': 0, 'c': 1}, 1),
        ({'a': 0, 'b': 1, 'c': 0}, 0),
        ({'a': 0, 'b': 1, 'c': 1}, 0),
        ({'a': 1, 'b': 0, 'c': 0}, 1),
        ({'a': 1, 'b': 0, 'c': 1}, 1),
        ({'a': 1, 'b': 1, 'c': 0}, 0),
        ({'a': 1, 'b': 1, 'c': 1}, 0),
    ]
    vars_list = ['a', 'b', 'c']

    # Тест покрывает метод Квайна
    primes = calculate_method(table, vars_list)
    assert "X0X" in primes

    # Тест покрывает таблично-расчетный метод
    tabular_calc_method(table, primes, vars_list)

    # Тест покрывает Карту Карно
    print_karnaugh_map(table, vars_list)

    # Тестируем Карту Карно для > 4 переменных (должна прерваться с сообщением)
    print_karnaugh_map(table, ['a', 'b', 'c', 'd', 'e'])
    captured = capsys.readouterr()
    assert "только до 4 переменных" in captured.out


def test_covers_and_format():
    assert covers("X01", "001") is True
    assert covers("X01", "011") is False

    cover = ["X01", "1X0"]
    formatted = format_final_mdnf(cover, ['a', 'b', 'c'])
    assert formatted == "(¬b & c) v (a & ¬c)"

    assert format_final_mdnf([], ['a']) == "0"


# ========================
# ТЕСТ ДЛЯ MAIN.PY
# ========================
@patch('builtins.input', return_value="a & (b v c)")
def test_main_function(mocked_input, capsys):
    main()
    captured = capsys.readouterr()

    assert "Обнаружены переменные: ['a', 'b', 'c']" in captured.out
    assert "Таблица истинности:" in captured.out
    assert "СДНФ:" in captured.out
    assert "СКНФ:" in captured.out
    assert "Полином Жегалкина:" in captured.out
    assert "классам Поста" in captured.out
    assert "Булева дифференциация" in captured.out
    assert "Расчетный метод (склеивание)" in captured.out
    assert "Карта Карно" in captured.out