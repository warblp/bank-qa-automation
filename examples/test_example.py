"""
Небольшой пример на unittest — используется как тестовый файл,
который телеграм-бот принимает и прогоняет в Docker-контейнере
(см. telegram-bot/bot.py -> run_docker_tests).
"""
import unittest


class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        self.assertEqual('hello'.upper(), 'HELLO')

    def test_isupper(self):
        self.assertTrue('HELLO'.isupper())
        self.assertFalse('Hello'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()
