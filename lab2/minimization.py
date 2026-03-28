from config import *


def get_binary_implicants(table: list, is_dnf: bool = True) -> list:
    """Получает бинарные представления конституент единицы (для ДНФ) или нуля (для КНФ)."""
    target = VAL_TRUE if is_dnf else VAL_FALSE
    return [bin(i)[2:].zfill(len(table[0][0])) for i, (_, res) in enumerate(table) if res == target]


def glue_step(implicants: list) -> tuple:
    """Выполняет один шаг склеивания импликант."""
    new_implicants, used = set(), set()
    for i in range(len(implicants)):
        for j in range(i + 1, len(implicants)):
            diff_idx = get_diff_index(implicants[i], implicants[j])
            if diff_idx != -1:
                glued = implicants[i][:diff_idx] + 'X' + implicants[i][diff_idx + 1:]
                new_implicants.add(glued)
                used.update([implicants[i], implicants[j]])
    return list(new_implicants), list(set(implicants) - used)


def get_diff_index(s1: str, s2: str) -> int:
    """Находит индекс единственного различающегося символа."""
    diffs = [i for i in range(len(s1)) if s1[i] != s2[i]]
    return diffs[0] if len(diffs) == 1 else -1


def calculate_method(table: list, variables: list, is_dnf: bool = True) -> list:
    """Расчетный метод. Выводит этапы склеивания и итоговую функцию."""
    form_name = "МДНФ" if is_dnf else "МКНФ"
    current_impls = get_binary_implicants(table, is_dnf)
    all_primes = []

    while True:
        print(f"Текущие импликанты ({form_name}): {current_impls}")
        next_impls, un_glued = glue_step(current_impls)
        all_primes.extend(un_glued)
        if not next_impls:
            all_primes.extend(current_impls)
            break
        current_impls = next_impls

    final_primes = list(set(all_primes))
    print(f"Первичные импликанты ({form_name}): {final_primes}")

    min_cover = get_minimal_cover(final_primes, get_binary_implicants(table, is_dnf))
    print(f"Результат расчетного метода ({form_name}): {format_final_form(min_cover, variables, is_dnf)}")
    return final_primes


def tabular_calc_method(table: list, prime_impls: list, variables: list, is_dnf: bool = True) -> None:
    """Расчетно-табличный метод. Выводит таблицу перекрытий и итоговую функцию."""
    form_name = "МДНФ" if is_dnf else "МКНФ"
    target_bin = get_binary_implicants(table, is_dnf)
    if not target_bin:
        res = "0" if is_dnf else "1"
        return print(f"Функция равна {res}. ({form_name})")

    header = "Импл. \\ Конст. | " + " | ".join(target_bin)
    print(header)
    print("-" * len(header))

    for prime in prime_impls:
        marks = ["X" if covers(prime, t) else " " for t in target_bin]
        print(f"{prime:13} | " + " | ".join(f"{m:{len(target_bin[0])}}" for m in marks))

    min_cover = get_minimal_cover(prime_impls, target_bin)
    print(f"\nРезультат таблично-расчетного метода ({form_name}): {format_final_form(min_cover, variables, is_dnf)}")


def print_karnaugh_map(table: list, variables: list) -> None:
    """Табличный метод (Карта Карно). Отрисовывает карту и выводит функции."""
    num_vars = len(variables)
    if num_vars > 4:
        return print("Карта Карно визуализируется только до 4 переменных.")

    gray_1, gray_2 = ['0', '1'], ['00', '01', '11', '10']
    rows, cols = (gray_1, gray_1) if num_vars == 2 else (gray_1, gray_2) if num_vars == 3 else (gray_2, gray_2)

    print("   | " + " | ".join(cols) + " |")
    for r in rows:
        row_out = f"{r} | "
        for c in cols:
            idx = int(r + c, 2)
            row_out += f" {table[idx][1]} | " if num_vars > 2 else f"{table[idx][1]} | "
        print(row_out)

    primes_dnf = get_prime_implicants_quiet(table, True)
    min_cover_dnf = get_minimal_cover(primes_dnf, get_binary_implicants(table, True))
    print(f"\nРезультат по Карте Карно (МДНФ): {format_final_form(min_cover_dnf, variables, True)}")

    primes_knf = get_prime_implicants_quiet(table, False)
    min_cover_knf = get_minimal_cover(primes_knf, get_binary_implicants(table, False))
    print(f"Результат по Карте Карно (МКНФ): {format_final_form(min_cover_knf, variables, False)}")


def covers(prime: str, minterm: str) -> bool:
    """Проверяет, покрывает ли импликанта минтерм."""
    return all(p == 'X' or p == m for p, m in zip(prime, minterm))


def get_prime_implicants_quiet(table: list, is_dnf: bool = True) -> list:
    """Получение импликант без принтов для Карты Карно"""
    current_impls = get_binary_implicants(table, is_dnf)
    all_primes = []
    while True:
        next_impls, un_glued = glue_step(current_impls)
        all_primes.extend(un_glued)
        if not next_impls:
            return list(set(all_primes + current_impls))
        current_impls = next_impls


def get_minimal_cover(prime_impls: list, target_bin: list) -> list:
    """Жадный алгоритм поиска минимального покрытия минтермов."""
    uncovered = set(target_bin)
    cover = []
    for term in target_bin:
        covering = [p for p in prime_impls if covers(p, term)]
        if len(covering) == 1 and covering[0] not in cover:
            cover.append(covering[0])
            uncovered -= {m for m in target_bin if covers(covering[0], m)}
    for p in prime_impls:
        if not uncovered: break
        if p not in cover and any(covers(p, m) for m in uncovered):
            cover.append(p)
            uncovered -= {m for m in target_bin if covers(p, m)}
    return cover


def format_final_form(cover: list, variables: list, is_dnf: bool = True) -> str:
    """Переводит бинарные маски покрытия обратно в строку букв."""
    if not cover:
        return "0" if is_dnf else "1"

    terms = []
    for impl in cover:
        parts = []
        for i, c in enumerate(impl):
            if c != 'X':
                if is_dnf:
                    parts.append(variables[i] if c == '1' else f"¬{variables[i]}")
                else:
                    parts.append(variables[i] if c == '0' else f"¬{variables[i]}")

        if is_dnf:
            terms.append("(" + " & ".join(parts) + ")" if parts else "(1)")
        else:
            terms.append("(" + " v ".join(parts) + ")" if parts else "(0)")

    return " v ".join(terms) if is_dnf else " & ".join(terms)