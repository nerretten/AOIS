class Node:
    """Узел классического связного списка."""

    def __init__(self, key, data, l_flag=0):
        self.ID = key
        self.Pi = data
        self.L = l_flag
        self.next = None


class HashTable:
    def __init__(self, size=20, base_address=1000):
        self.size = size
        self.B = base_address
        self.table = [None] * self.size
        self.count = 0

        self.external_memory = {}
        self.memory_pointer_counter = 8000

    def _calculate_v(self, key):
        return sum(ord(char) for char in str(key))

    def _hash(self, v):
        return v % self.size

    def _get_physical_address(self, h_idx):
        """Вычисление имитированного физического адреса с учетом B"""
        return self.B + h_idx

    def _prepare_data(self, data):
        """Вспомогательный метод для обработки длинных данных"""
        if len(str(data)) > 15:
            ptr = f"MEM_{self.memory_pointer_counter}"
            self.external_memory[ptr] = data
            self.memory_pointer_counter += 1
            return ptr, 1
        return data, 0

    def insert(self, key, data):
        """Создание новой записи"""
        v = self._calculate_v(key)
        h_idx = self._hash(v)
        phys_addr = self._get_physical_address(h_idx)

        current = self.table[h_idx]
        while current:
            if current.ID == key:
                print(f"[-] Ошибка: Термин '{key}' уже существует. Используйте функцию обновления.\n")
                return
            current = current.next

        pi_content, l_flag = self._prepare_data(data)
        new_node = Node(key, pi_content, l_flag)

        if self.table[h_idx] is None:
            self.table[h_idx] = new_node
            print(f"[+] '{key}' добавлен. Логический индекс: {h_idx}, Физический адрес: {phys_addr}")
        else:
            new_node.next = self.table[h_idx]
            self.table[h_idx] = new_node
            print(f"[!] Коллизия разрешена. '{key}' добавлен в цепочку по адресу {phys_addr}.")

        self.count += 1

    def update(self, key, new_data):
        """Обновление существующей записи (Update)."""
        v = self._calculate_v(key)
        h_idx = self._hash(v)

        current = self.table[h_idx]
        while current:
            if current.ID == key:
                pi_content, l_flag = self._prepare_data(new_data)
                current.Pi = pi_content
                current.L = l_flag
                print(f"[+] Данные для термина '{key}' успешно обновлены.\n")
                return True
            current = current.next

        print(f"[-] Термин '{key}' для обновления не найден.\n")
        return False

    def search(self, key):
        """Поиск (Read)."""
        v = self._calculate_v(key)
        h_idx = self._hash(v)

        current = self.table[h_idx]
        while current:
            if current.ID == key:
                if current.L == 1:
                    real_data = self.external_memory.get(current.Pi, "ОШИБКА")
                    print(f"[*] Найдено: '{key}' -> {real_data} \n")
                    return real_data
                else:
                    print(f"[*] Найдено: '{key}' -> {current.Pi}\n")
                    return current.Pi
            current = current.next

        print(f"[-] Термин '{key}' не найден.\n")
        return None

    def delete(self, key):
        v = self._calculate_v(key)
        h_idx = self._hash(v)

        current = self.table[h_idx]
        prev = None

        while current:
            if current.ID == key:
                if prev is None:
                    self.table[h_idx] = current.next
                else:
                    prev.next = current.next

                self.count -= 1
                print(f"[+] Термин '{key}' удален из таблицы.\n")
                return True
            prev = current
            current = current.next

        print(f"[-] Невозможно удалить: термин '{key}' не найден.\n")
        return False

    def display(self):
        print("-" * 80)
        print(f"{'Idx':<4} | {'Phys Addr':<10} | {'Linked List (ID -> ID -> ...)'}")
        print("-" * 80)
        for i in range(self.size):
            phys_addr = self._get_physical_address(i)
            chain = []
            current = self.table[i]
            while current:
                chain.append(f"[{current.ID}]")
                current = current.next

            chain_str = " -> ".join(chain) if chain else "Пусто"
            print(f"{i:<4} | {phys_addr:<10} | {chain_str}")
        print("-" * 80)
        print(f"Всего элементов: {self.count}\n")