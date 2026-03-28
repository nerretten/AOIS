import itertools

from parser import build_rpn, extract_variables
from evaluator import build_truth_table, print_truth_table
from normal_forms import get_sdnf, get_sknf, get_numeric_forms, get_index_form, check_post_classes
from analyzer import get_zhegalkin_coeffs, build_zhegalkin_poly, find_fictitious_vars, get_mixed_derivative
from minimization import calculate_method, tabular_calc_method, print_karnaugh_map


def main():
    expression = input("Введите логическую функци:")
    print(f"Исходная функция: {expression}")

    rpn_expr = build_rpn(expression)
    variables = extract_variables(rpn_expr)
    print(f"Обнаружены переменные: {variables}\n")

    # 2. Построение таблицы истинности
    truth_table = build_truth_table(rpn_expr, variables)
    print("Таблица истинности:")
    print_truth_table(truth_table, variables)

    # 3. СДНФ и СКНФ
    sdnf_str = get_sdnf(truth_table, variables)
    sknf_str = get_sknf(truth_table, variables)
    print(f"\nСДНФ: {sdnf_str}")
    print(f"СКНФ: {sknf_str}")

    # 4. Числовая форма
    ones_idx, zeros_idx = get_numeric_forms(truth_table)
    print(f"\nЧисловая форма СДНФ: v({', '.join(map(str, ones_idx))})")
    print(f"Числовая форма СКНФ: &({', '.join(map(str, zeros_idx))})")

    # 5. Индексная форма
    index_form = get_index_form(truth_table)
    print(f"\nИндексная форма функции: {index_form}")

    # 6. Полином Жегалкина
    zheg_coeffs = get_zhegalkin_coeffs(truth_table)
    zhegalkin_str = build_zhegalkin_poly(zheg_coeffs, variables)
    print(f"\nПолином Жегалкина: {zhegalkin_str}")

    # 7. Классы Поста
    post_classes = check_post_classes(truth_table, zheg_coeffs)
    print(f"\nПринадлежность к классам Поста (T0, T1, S, M, L): {post_classes}")

    # 8. Фиктивные переменные
    fictitious = find_fictitious_vars(truth_table, variables)
    print(f"\nФиктивные переменные: {fictitious if fictitious else 'Нет'}")

    # 9. Булева дифференциация
    print("\n Булева дифференциация ")
    max_order = min(len(variables) + 1, 5)
    for order in range(1, max_order):
        for combo in itertools.combinations(variables, order):
            deriv = get_mixed_derivative(truth_table, list(combo), variables)
            combo_str = "".join(combo)
            print(f"d^{order}f / d({combo_str}): {deriv}")

    # 10. Расчетный метод
    print("\n Расчетный метод (склеивание) ")
    print("--- Для МДНФ ---")
    prime_implicants_dnf = calculate_method(truth_table, variables, is_dnf=True)
    print("\n--- Для МКНФ ---")
    prime_implicants_knf = calculate_method(truth_table, variables, is_dnf=False)

    # 11. Расчетно-табличный метод
    print("\n Расчетно-табличный метод")
    print("--- Для МДНФ ---")
    tabular_calc_method(truth_table, prime_implicants_dnf, variables, is_dnf=True)
    print("\n--- Для МКНФ ---")
    tabular_calc_method(truth_table, prime_implicants_knf, variables, is_dnf=False)

    # 12. Карты Карно
    print("\nТабличный метод (Карта Карно) ")
    print_karnaugh_map(truth_table, variables)


if __name__ == "__main__":
    main()