"""Здесь полностью исправленные и рабочие тесты в состоянии
до объединения 3-ех тестов в один.(вдруг Игорь скажет все вернуть так)
"""

from http import HTTPStatus

from django.urls import reverse

from notes.tests.conftest import FixtursForTests


class TestRoutes(FixtursForTests):
    """Тест маршрутизации."""

    def test_no_auth_user(self):
        """Проверка доступа неавторизованного пользователя.

        Анонимный пользователь имеет доступ к следующим страницам:
        главная, входа, выхода, регистрации.
        """
        urls = (
            (self.url_home),
            (self.url_login),
            (self.url_logout),
            (self.url_signup),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user(self):
        """Проверка доступа авторизованного пользователя.

        Авторизованный пользователь имеет доступ к страницам:
        notes/ - список заметок.
        add/ - добавление новой заметки.
        done/ - успешное уведомление новой заметки.
        """
        urls = (
            (self.url_notes),
            (self.url_add_note),
            (self.url_success),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_read_update_delete(self):
        """Проверка просмотра, удаления, редактирования заметки.

        Автору доступны страницы:
        просмотра, редактирования, удаления заметки.
        Для другого польователя эти страницы недоступны.
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in (self.url_detail, self.url_edit, self.url_delete):
                with self.subTest(user=user, url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка анонимного пользователя.

        При запросе к данным страницам анонимный пользователь
        должен быть перенаправлен на страницу входа.
        """
        login_url = reverse('users:login')
        urls = (
            (self.url_notes),
            (self.url_success),
            (self.url_add_note),
            (self.url_detail),
            (self.url_edit),
            (self.url_delete),
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
