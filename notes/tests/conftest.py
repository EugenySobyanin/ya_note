from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

Users = get_user_model()


class FixtursForTests(TestCase):
    """Собраны фикстуры для всего модуля."""

    @classmethod
    def setUpTestData(cls) -> None:
        # Два пользователя и два клиента
        cls.author = Users.objects.create(username='Автор заметки.')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = Users.objects.create(username='Не автор заметки.')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Две заметки от каждого пользователя
        cls.note = Note.objects.create(
            title="Название",
            text="Текст",
            slug="xxxaaaxxx",
            author=cls.author
        )
        cls.note_by_reader = Note.objects.create(
            title="Другое название",
            text="Другой текст",
            slug="yyyxxxyyy",
            author=cls.reader
        )
        # реверсы
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_signup = reverse('users:signup')
        cls.url_home = reverse('notes:home')
        cls.url_notes = reverse('notes:list')
        cls.url_add_note = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.url_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug, ))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug, ))

        # данные для формы
        cls.form_data = {
            'title': 'Некое название',
            'text': 'Некий текст.'
        }
