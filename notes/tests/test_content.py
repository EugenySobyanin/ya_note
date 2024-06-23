from notes.forms import NoteForm
from notes.tests.conftest import FixtursForTests


class TestContent(FixtursForTests):
    """Тест содержимого на страницах проекта."""

    def test_note_in_note_list(self):
        """Объект заметки передается шаблон."""
        response = self.author_client.get(self.url_notes)
        self.assertIn(self.note, response.context['object_list'])

    def test_user_list(self):
        """У пользователя нет заметок другого пользователя."""
        response = self.author_client.get(self.url_notes)
        self.assertNotIn(
            self.note_by_reader,
            response.context['object_list']
        )

    def test_authorized_client_has_form(self):
        """Проверка есть ли форма на страницах создания и удаления заметок."""
        urls = (
            (self.url_add_note),
            (self.url_edit),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
