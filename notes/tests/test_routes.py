from http import HTTPStatus

from django.urls import reverse

from notes.tests.conftest import FixtursForTests


class TestRoutes(FixtursForTests):
    """Тест маршрутизации."""

    def test_availability_pages(self):
        """Проверка всех маршрутов."""
        data = (
            (self.url_home, self.client, HTTPStatus.OK),
            (self.url_login, self.client, HTTPStatus.OK),
            (self.url_logout, self.client, HTTPStatus.OK),
            (self.url_signup, self.client, HTTPStatus.OK),
            (self.url_notes, self.author_client, HTTPStatus.OK),
            (self.url_add_note, self.author_client, HTTPStatus.OK),
            (self.url_success, self.author_client, HTTPStatus.OK),
            (self.url_detail, self.author_client, HTTPStatus.OK),
            (self.url_edit, self.author_client, HTTPStatus.OK),
            (self.url_delete, self.author_client, HTTPStatus.OK),
            (self.url_detail, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.url_edit, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.url_delete, self.reader_client, HTTPStatus.NOT_FOUND),
        )

        for url, user_client, status in data:
            with self.subTest(url=url, user_client=user_client, status=status):
                response = user_client.get(url)
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
