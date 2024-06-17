from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create(username='Автор1')
        cls.user2 = User.objects.create(username='Автор2')
        cls.note = Note.objects.create(
            title="Название",
            text="Текст",
            slug="xxxaaaxxx",
            author=cls.user1
        )
        cls.note2 = Note.objects.create(
            title="Название2",
            text="Текст2",
            slug="yyyyy",
            author=cls.user2
        )
        
    def test_note_in_note_list(self):
        """Проверят, что объекта заметки передается шаблон."""
        self.client.force_login(self.user1)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        
    def test_user_list(self):
        """Проверяет, что у пользователя нет заметок другого пользователя."""
        self.client.force_login(self.user1)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note2, object_list)
        
    def test_authorized_client_has_form(self):
        """Проверяем есть ли форма на страницах создания и удаления заметок."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, arg in urls:
            with self.subTest():
                self.client.force_login(self.user1)
                url = reverse(name, args=arg)
                response = self.client.get(url)
                self.assertIn('form', response.context)