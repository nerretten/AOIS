import unittest
from unittest.mock import patch
from io import StringIO
import sys

from hash_table import HashTable, Node
from main import pre_populate, menu


class TestTrueHashTable(unittest.TestCase):
    def setUp(self):
        """Создаем новую пустую таблицу перед каждым тестом."""
        self.ht = HashTable(size=20, base_address=1000)
        # Отключаем вывод print в консоль во время тестов, чтобы не засорять экран
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        """Возвращаем стандартный вывод после тестов."""
        sys.stdout = self.held

    def test_calculate_v_and_hash(self):
        """Тест вычисления значения V(K) и логического хеша."""
        v = self.ht._calculate_v("A")
        self.assertEqual(v, 65)  # ASCII 'A' = 65
        self.assertEqual(self.ht._hash(65), 5)  # 65 % 20 = 5
        self.assertEqual(self.ht._get_physical_address(5), 1005)

    def test_insert_and_search_short_data(self):
        """Тест вставки и поиска коротких данных (L=0)."""
        self.ht.insert("TestKey", "Short")
        self.assertEqual(self.ht.search("TestKey"), "Short")

        # Проверка внутренней структуры
        idx = self.ht._hash(self.ht._calculate_v("TestKey"))
        node = self.ht.table[idx]
        self.assertEqual(node.L, 0)
        self.assertEqual(self.ht.count, 1)

    def test_insert_and_search_long_data(self):
        """Тест вставки и поиска длинных данных (внешняя память, L=1)."""
        long_data = "Это очень длинная строка для проверки внешней памяти"
        self.ht.insert("LongKey", long_data)

        self.assertEqual(self.ht.search("LongKey"), long_data)

        # Проверка внутренней структуры
        idx = self.ht._hash(self.ht._calculate_v("LongKey"))
        node = self.ht.table[idx]
        self.assertEqual(node.L, 1)
        self.assertTrue(node.Pi.startswith("MEM_"))
        self.assertEqual(self.ht.external_memory[node.Pi], long_data)

    def test_insert_duplicate(self):
        """Тест защиты от добавления дубликатов."""
        self.ht.insert("Key1", "Data1")
        self.ht.insert("Key1", "Data2")  # Попытка добавить дубликат

        self.assertEqual(self.ht.count, 1)
        self.assertEqual(self.ht.search("Key1"), "Data1")  # Данные не должны были измениться

    def test_collisions(self):
        """Тест разрешения коллизий (построение связного списка)."""
        # "A" (65), "U" (85), "i" (105) дают остаток 5 при делении на 20
        self.ht.insert("A", "Data A")
        self.ht.insert("U", "Data U")
        self.ht.insert("i", "Data i")

        self.assertEqual(self.ht.count, 3)
        self.assertEqual(self.ht.search("A"), "Data A")
        self.assertEqual(self.ht.search("U"), "Data U")
        self.assertEqual(self.ht.search("i"), "Data i")

    def test_update_existing_and_missing(self):
        """Тест операции обновления данных."""
        self.ht.insert("Key1", "OldData")

        # Обновляем на короткие данные
        self.assertTrue(self.ht.update("Key1", "NewData"))
        self.assertEqual(self.ht.search("Key1"), "NewData")

        # Обновляем на длинные данные (проверка переключения флага L)
        self.assertTrue(self.ht.update("Key1", "Очень длинные новые данные"))
        self.assertEqual(self.ht.search("Key1"), "Очень длинные новые данные")

        # Обновление несуществующего ключа
        self.assertFalse(self.ht.update("Ghost", "Data"))

    def test_delete_nodes(self):
        """Тест удаления из разных частей связного списка."""
        self.ht.insert("A", "Data A")  # Конец списка
        self.ht.insert("U", "Data U")  # Середина
        self.ht.insert("i", "Data i")  # Начало (голова списка)

        # 1. Удаляем из середины
        self.assertTrue(self.ht.delete("U"))
        self.assertIsNone(self.ht.search("U"))
        self.assertEqual(self.ht.count, 2)

        # 2. Удаляем голову
        self.assertTrue(self.ht.delete("i"))
        self.assertIsNone(self.ht.search("i"))
        self.assertEqual(self.ht.count, 1)

        # 3. Удаляем последний элемент
        self.assertTrue(self.ht.delete("A"))
        self.assertIsNone(self.ht.search("A"))
        self.assertEqual(self.ht.count, 0)

        # 4. Удаляем несуществующий
        self.assertFalse(self.ht.delete("Ghost"))

    def test_search_missing_and_corrupted(self):
        """Тест поиска отсутствующих элементов и поврежденной внешней памяти."""
        self.assertIsNone(self.ht.search("Ghost"))

        # Имитируем утерю данных во внешней памяти
        self.ht.insert("Long", "Very long string here")
        self.ht.external_memory.clear()
        self.assertEqual(self.ht.search("Long"), "ОШИБКА")

    def test_display(self):
        """Тест метода визуализации (проверка на отсутствие ошибок при вызове)."""
        self.ht.insert("A", "Data A")
        self.ht.insert("LongKey", "Very long data for L flag testing")

        # Перенаправляем вывод для проверки содержимого
        captured_output = StringIO()
        sys.stdout = captured_output
        self.ht.display()

        output = captured_output.getvalue()
        print(output)
        self.assertIn("[A]", output)
        self.assertIn("[LongKey]", output)

    def test_pre_populate(self):
        """Тест функции предварительного заполнения."""
        pre_populate(self.ht)
        self.assertEqual(self.ht.count, 10)

    @patch('builtins.input', side_effect=[
        '9',  # Неверный ввод
        '1',  # Показать структуру
        '2', 'New', 'Val',  # Добавить
        '3', 'New',  # Найти
        '4', 'New', 'Upd',  # Обновить
        '5', 'New',  # Удалить
        '6'  # Выход
    ])
    def test_menu(self, mock_input):
        """Тест интерактивного меню (симуляция ввода пользователя)."""
        # Меню само вызывает принты, так что просто проверяем, что оно не падает
        menu()
        self.assertTrue(True)  # Если дошли сюда без исключений, тест пройден


if __name__ == '__main__':
    unittest.main()