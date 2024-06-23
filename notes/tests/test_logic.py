from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestСreateNote(TestCase):
    """Проверка создания заметки.

    Класс тестирует поведение приложения
    при различных вариантах создания заметки.
    """

    NOTE_TITLE = "Название."
    NOTE_TEXT = "Текст заметки."

    @classmethod
    def setUpTestData(cls) -> None:
        cls.client_auth = Client()
        cls.author = User.objects.create(username="Автор заметки.")
        cls.client_auth.force_login(cls.author)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }

    def test_auth_user_create_note_and_not_similar_slugs(self):
        """Проверка создания заметки.

        Проверка, что авторизованный пользователь может создать заметку.
        Проверка, что не может быть двух заметок с одинаковым slug.
        """
        self.client_auth.post(self.url, data=self.form_data)
        self.client_auth.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_anonim_user_cant_create_note(self):
        """Проверка создания заметки.

        Проверка, что анонимный пользователь не может создать заметку.
        """
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_empty_slug_field(self):
        """Проверка создания заметки.

        Проверка, что при создании заметки с пустым полем slug
        сработает функция slugify для названия заметки.
        """
        self.client_auth.post(self.url, data=self.form_data)
        # Получение максимальной длины поля из модели.
        max_slug_length = Note._meta.get_field('slug').max_length
        excepted_slug = slugify(self.NOTE_TITLE)[:max_slug_length]
        self.assertEqual(Note.objects.get(pk=1).slug, excepted_slug)


class TestUpdateDeleteNote(TestCase):
    """Проверка редактирования и удаления заметок.

    Проверка редактирования и удаления заметок пользователем
    и проверка попытки редакетирования и удаления чужих заметок.
    """

    NOTE_TITLE = "Название."
    NOTE_TEXT = "Текст заметки."
    CHANGE_TITLE = "Другое название."
    CHANGE_TEXT = "Другой текст."

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username="Автор")
        cls.reader = User.objects.create(username="Читатель")
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
        )
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.CHANGE_TITLE,
            'text': cls.CHANGE_TEXT,
        }

    def test_author_update_note(self):
        """Пользователь может редактировать свои заметки."""
        self.author_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.CHANGE_TITLE)
        self.assertEqual(self.note.text, self.CHANGE_TEXT)

    def test_author_delete_note(self):
        """Пользователь может удалять свои заметки."""
        self.author_client.delete(self.delete_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_reader_cant_update_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.reader_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_reader_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
