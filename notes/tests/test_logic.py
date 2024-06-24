from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.conftest import FixtursForTests


class TestСreateNote(FixtursForTests):
    """Проверка создания заметки.

    Класс тестирует поведение приложения
    при различных вариантах создания заметки.
    """

    def test_auth_user_create_note_and_not_similar_slugs(self):
        """Авторизованный пользователь может создать заметку."""
        Note.objects.all().delete()
        self.author_client.post(self.url_add_note, data=self.form_data)
        note_from_bd = Note.objects.get()
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(note_from_bd.title, self.form_data['title'])
        self.assertEqual(note_from_bd.text, self.form_data['text'])
        self.assertEqual(note_from_bd.author, self.author)

    def test_not_similar_slugs(self):
        """Проверка унакальности slug при создании заметки."""
        note_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(
            self.url_add_note, data=self.form_data
        )
        self.assertEqual(Note.objects.count(), note_count)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{self.note.slug}{WARNING}'
        )

    def test_anonim_user_cant_create_note(self):
        """Проверка создания заметки.

        Проверка, что анонимный пользователь не может создать заметку.
        """
        Note.objects.all().delete()
        self.client.post(self.url_add_note, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_empty_slug_field(self):
        """Проверка создания заметки.

        Проверка, что при создании заметки с пустым полем slug
        сработает функция slugify для названия заметки.
        """
        Note.objects.all().delete()
        self.author_client.post(self.url_add_note, data=self.form_data)
        excepted_slug = slugify(self.form_data['title'])
        self.assertEqual(Note.objects.get().slug, excepted_slug)


class TestUpdateDeleteNote(FixtursForTests):
    """Проверка редактирования и удаления заметок.

    Проверка редактирования и удаления заметок пользователем
    и проверка попытки редакетирования и удаления чужих заметок.
    """

    def test_author_update_note(self):
        """Пользователь может редактировать свои заметки."""
        self.author_client.post(self.url_edit, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.author, self.author)

    def test_author_delete_note(self):
        """Пользователь может удалять свои заметки."""
        note_count = Note.objects.count()
        self.author_client.delete(self.url_delete)
        self.assertEqual(Note.objects.count(), note_count - 1)

    def test_reader_cant_update_note(self):
        """Пользователь не может редактировать чужие заметки."""
        self.reader_client.post(self.url_edit, data=self.form_data)
        note_from_bd = Note.objects.get(id=1)
        self.assertEqual(note_from_bd.title, self.note.title)
        self.assertEqual(note_from_bd.text, self.note.text)
        self.assertEqual(note_from_bd.author, self.note.author)

    def test_reader_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        note_count = Note.objects.count()
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_count)
