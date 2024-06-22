from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Тест содержимого на страницах проекта."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create(username='Автор1')
        cls.another_user = User.objects.create(username='Автор2')
        cls.client_user = Client()
        cls.client_user.force_login(cls.user)
        cls.url_notes_list = reverse('notes:list')
        cls.response = cls.client_user.get(cls.url_notes_list)
        cls.object_list = cls.response.context['object_list']
        cls.note = Note.objects.create(
            title="Название",
            text="Текст",
            slug="xxxaaaxxx",
            author=cls.user
        )
        cls.note2 = Note.objects.create(
            title="Название2",
            text="Текст2",
            slug="yyyyy",
            author=cls.another_user
        )

    def test_note_in_note_list(self):
        """Объект заметки передается шаблон."""
        self.assertIn(self.note, self.object_list)

    def test_user_list(self):
        """У пользователя нет заметок другого пользователя."""
        self.assertNotIn(self.note2, self.object_list)

    def test_authorized_client_has_form(self):
        """Проверка есть ли форма на страницах создания и удаления заметок."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, arg in urls:
            with self.subTest():
                url = reverse(name, args=arg)
                response = self.client_user.get(url)
                self.assertIn('form', response.context)
