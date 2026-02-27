import pytest
from unittest.mock import patch
import io

from basic_operations import (
    decimal_to_binary, from_binary_to_decimal, decimal_to_ones_complement,
    twos_complement, add_binary, minus_binary, multiply, divide, clean_zeros, is_greater_or_equal
)
from ieee import (
    float_to_ieee_bin, ieee_bin_to_float, add_ieee, multiply_ieee, divide_ieee
)
from bcd_2421 import int_to_2421_array, array_2421_to_int, add_2421_numbers
from main import main



@pytest.mark.parametrize("dec, expected_sign", [(5, 0), (-5, 1), (0, 0)])
def test_decimal_to_binary_and_back(dec, expected_sign):
    bin_arr = decimal_to_binary(dec)
    assert bin_arr[0] == expected_sign
    assert len(bin_arr) == 32
    assert from_binary_to_decimal(bin_arr) == dec


def test_ones_complement():
    pos = decimal_to_ones_complement(5)
    assert pos == decimal_to_binary(5)
    neg = decimal_to_ones_complement(-5)
    assert neg[0] == 1
    assert neg[31] == 0


def test_twos_complement():
    pos = twos_complement(decimal_to_binary(5))
    assert pos == decimal_to_binary(5)

    neg_bin = decimal_to_binary(-5)
    neg_tc = twos_complement(neg_bin)
    back_to_bin = twos_complement(neg_tc)
    assert back_to_bin == neg_bin


@pytest.mark.parametrize("x1, x2, expected", [
    (10, 5, 15), (-10, 5, -5), (10, -5, 5), (-10, -5, -15), (0, 0, 0)
])
def test_add_minus_binary(x1, x2, expected):
    res_add = add_binary(x1, x2)
    assert from_binary_to_decimal(res_add) == expected

    res_minus = minus_binary(x1, -x2)
    assert from_binary_to_decimal(res_minus) == expected


@pytest.mark.parametrize("x1, x2, expected", [
    (3, 4, 12), (-3, 4, -12), (3, -4, -12), (-3, -3, 9), (0, 5, 0), (5, 0, 0)
])
def test_multiply(x1, x2, expected):
    res = multiply(x1, x2)
    assert from_binary_to_decimal(res) == expected


def test_divide():
    sign, int_part, float_part = divide(10, 2)
    assert sign == 0
    assert clean_zeros(int_part) == [1, 0, 1]

    sign, _, _ = divide(-10, 2)
    assert sign == 1

    with pytest.raises(ZeroDivisionError):
        divide(10, 0)



@pytest.mark.parametrize("f", [1.5, -1.5, 0.0, 0.15625, 123.456])
def test_float_ieee_conversion(f):
    bin_arr = float_to_ieee_bin(f)
    assert len(bin_arr) == 32
    res_f = ieee_bin_to_float(bin_arr)
    assert round(res_f, 3) == round(f, 3)


@pytest.mark.parametrize("f1, f2, expected", [
    (1.5, 2.5, 4.0),
    (2.5, -1.5, 1.0),
    (-2.0, -2.0, -4.0),
    (0.0, 5.0, 5.0)
])
def test_add_ieee(f1, f2, expected):
    b1 = float_to_ieee_bin(f1)
    b2 = float_to_ieee_bin(f2)
    res = add_ieee(b1, b2)
    assert round(ieee_bin_to_float(res), 3) == expected


@pytest.mark.parametrize("f1, f2, expected", [
    (1.5, 2.0, 3.0), (-1.5, 2.0, -3.0), (0.0, 5.0, 0.0)
])
def test_multiply_ieee(f1, f2, expected):
    b1 = float_to_ieee_bin(f1)
    b2 = float_to_ieee_bin(f2)
    res = multiply_ieee(b1, b2)
    assert round(ieee_bin_to_float(res), 3) == expected


def test_divide_ieee():
    b1 = float_to_ieee_bin(5.0)
    b2 = float_to_ieee_bin(2.0)
    res = divide_ieee(b1, b2)
    assert ieee_bin_to_float(res) == 2.5

    with pytest.raises(ZeroDivisionError):
        divide_ieee(b1, float_to_ieee_bin(0.0))

    res_zero = divide_ieee(float_to_ieee_bin(0.0), b2)
    assert ieee_bin_to_float(res_zero) == 0.0


# ==========================================
# ТЕСТЫ ДЛЯ bcd_2421.py
# ==========================================

@pytest.mark.parametrize("num, expected", [
    (5, [[1, 0, 1, 1]]),
    (15, [[0, 0, 0, 1], [1, 0, 1, 1]]),
    (0, [[0, 0, 0, 0]])
])
def test_2421_conversion(num, expected):
    arr = int_to_2421_array(num)
    assert arr == expected
    assert array_2421_to_int(arr) == num


def test_add_2421():
    arr1 = int_to_2421_array(15)
    arr2 = int_to_2421_array(27)
    res = add_2421_numbers(arr1, arr2)
    assert array_2421_to_int(res) == 42

    arr3 = int_to_2421_array(9)
    arr4 = int_to_2421_array(9)
    res_carry = add_2421_numbers(arr3, arr4)
    assert array_2421_to_int(res_carry) == 18




def test_main_menu_exit():
    with patch('builtins.input', side_effect=['0']):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main()
            assert "Завершение работы" in fake_out.getvalue()


def test_main_menu_operations():
    inputs = [
        '1', '5',
        '2', '10', '5',
        '5', '10', '0',
        '6', '1.5', '2.0', '+',
        '7', '15', '27',
        '8',
        '0'
    ]
    with patch('builtins.input', side_effect=inputs):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            assert "Прямой код" in output
            assert "Результат (10-ый): 15" in output
            assert "Ошибка: Деление на ноль!" in output
            assert "IEEE-754 (2-ый)" in output
            assert "Результат (2-ый 2421)" in output
            assert "Неверный ввод" in output