import unittest

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

Users = get_user_model()

class TestLogic(TestCase):
    NOTE_TEXT = "Текст заметки."
    
    @classmethod
    def setUpTestData(cls) -> None:
        cls.client_author = Client()
        cls.author = Users.objects.create(username="Автор заметки.")
        cls.client_author.force_login(cls.author)
        cls.note = Note.objects.create(text=cls.NOTE_TEXT, author=cls.author)
        cls.url = reverse('notes:detail', args=(cls.note.id,))
        cls.form_data = {'text': cls.NOTE_TEXT}
        
    def test_user_create_note(self):
        self.client_author.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        
    def test_anonim_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)
        
        
        
        
        
        
        