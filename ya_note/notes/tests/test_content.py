from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from notes.models import Note


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author_1 = User.objects.create(username='testuser_1')
        cls.author_2 = User.objects.create(username='testuser_2')
        cls.note_1 = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author_1)
        cls.note_2 = Note.objects.create(
            title='Заголовок 2',
            text='Текст 2',
            slug='slug_2',
            author=cls.author_2)

    def test_notes_list_for_different_users(self):
        url = reverse('notes:list')
        self.client.force_login(self.author_1)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note_1, object_list)
        self.assertNotIn(self.note_2, object_list)

    def test_create_note_page_contains_form(self):
        url = reverse('notes:add')
        self.client.force_login(self.author_1)
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        url = reverse('notes:edit', args={'slug': self.note_1.slug})
        self.client.force_login(self.author_1)
        response = self.client.get(url)
        self.assertIn('form', response.context)
