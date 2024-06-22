from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

Users = get_user_model()


class TestRoutes(TestCase):
    """Тест маршрутизации."""

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

    def test_no_auth_user(self):
        """Проверка доступа неавторизованного пользователя.

        Анонимный пользователь имеет доступ к следующим страницам:
        главная, входа, выхода, регистрации.
        """
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

    def test_auth_user(self):
        """Проверка доступа авторизованного пользователя.

        Авторизованный пользователь имеет доступ к страницам:
        notes/ - список заметок.
        add/ - добавление новой заметки.
        done/ - успешное уведомление новой заметки.
        """
        self.client.force_login(self.author)
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_read_update_delete(self):
        """Проверка просмотра, удаления, редактирования заметки.

        Автору доступны страницы:
        просмотра, редактирования, удаления заметки.
        Для другого польователя эти страницы недоступны.
        """
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
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка анонимного пользователя.

        При запросе к данным страницам анонимный пользователь
        должен быть перенаправлен на страницу входа.
        """
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
