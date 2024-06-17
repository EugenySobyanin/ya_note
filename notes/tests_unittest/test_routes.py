import unittest

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

Users = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = Users.objects.create(username="Автор")
        cls.reader = Users.objects.create(username="Читатель")
        cls.note = Note.objects.create(
            title="Название",
            text="Текст",
            slug="xxxaaaxxx",
            author=cls.author
        )

    # @unittest.skip(reason="Проходит.") 
    def test_a_availability_home_page(self):
        """Проверка, что не авторизированный пользователь имеет доступ к главной старнице."""
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        

    # @unittest.skip(reason="Проходит.")
    def test_b_availability_notes_add_done(self): 
        """Проверка, что авторизированному пользователю доступны страницы:
        notes/ - список заметок
        add/ - добавление новой заметки
        done/ - успешное уведомление новой заметки"""
        user = Users.objects.create(username='Пользоатель.')
        self.client.force_login(user)
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK, "Упал какой-то из вторых тестов.")

    # @unittest.skip(reason="Проходит.")                     
    def test_c_note_read_update_delete(self):
        """Проверка, что автора поста доступны страницы заметки, редактирования, удаления
        а не автору недоступны"""

        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status, f'Ошибка для {user.username} - маршрут {name}, notes_aвтор {self.note.author}')

    # @unittest.skip(reason="Проходит.")
    def test_redirect_for_anonymous_client(self):
        """Тест на переход анонимного пользователя на страницу логина при запросе к разным страницам."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, arg in urls:
            with self.subTest():
                url = reverse(name, args=arg)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
            
        