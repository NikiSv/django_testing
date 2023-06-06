from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify


class NoteCreation(TestCase):
    TITLE = 'Новый заголовок'
    TEXT = 'Новый текст'
    SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='testuser')
        cls.form_data = {'title': cls.TITLE,
                         'text': cls.TEXT,
                         'slug': cls.SLUG}

    def test_anonymous_user_cant_create_notes(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_notes(self):
        url = reverse('notes:add')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        notes = Note.objects.get()
        self.assertEqual(notes.text, self.TEXT)
        self.assertEqual(notes.title, self.TITLE)
        self.assertEqual(notes.slug, self.SLUG)
        self.assertEqual(notes.author, self.author)

    def test_not_unique_slug(self):
        self.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=self.author)
        url = reverse('notes:add')
        self.client.force_login(self.author)
        self.form_data['slug'] = self.notes.slug
        response = self.client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(
            self.notes.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        self.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=self.author)
        url = reverse('notes:edit', args={'slug': self.notes.slug})
        response = self.client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.TEXT)
        self.assertEqual(self.notes.title, self.TITLE)
        self.assertEqual(self.notes.slug, self.SLUG)

    def test_other_user_cant_edit_note(self):
        self.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=self.author)
        self.other_user = User.objects.create(username='other_user')
        self.client.force_login(self.other_user)
        url = reverse('notes:edit', args={'slug': self.notes.slug})
        response = self.client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.notes.id)
        self.assertEqual(self.notes.text, note_from_db.text)
        self.assertEqual(self.notes.title, note_from_db.title)
        self.assertEqual(self.notes.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=self.author)
        url = reverse('notes:delete', args={'slug': self.note.slug})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=self.author)
        self.other_user = User.objects.create(username='other_user')
        self.client.force_login(self.other_user)
        url = reverse('notes:edit', args={'slug': self.note.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
