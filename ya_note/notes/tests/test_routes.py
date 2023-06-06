from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from notes.models import Note


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,)

    def test_home_availability_for_anonymous_user(self):
        OK = HTTPStatus.OK
        urls = (
            ('notes:home', OK),
            ('users:login', OK),
            ('users:logout', OK),
            ('users:signup', OK),
        )
        for name, status in urls:
            with self.subTest(name=name, status=status):
                if self.client.force_login(self.author):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        for name in ('notes:add', 'notes:list', 'notes:success'):
            if self.client.force_login(self.author):
                with self.subTest(name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        for name in ('notes:edit', 'notes:edit', 'notes:delete'):
            if self.client.force_login(self.author):
                with self.subTest(name=name):
                    url = reverse(name, args={'slug': self.note.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
            else:
                with self.subTest(name=name):
                    url = reverse(name, args={'slug': self.note.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)

    def test_redirects(self):
        login_url = reverse('users:login')
        for name in ('notes:add',
                     'notes:list'
                     ):
            with self.subTest(name=name):
                url = reverse(name)
            for name in ('notes:edit',
                         'notes:delete',
                         'notes:detail'
                         ):
                with self.subTest(name=name):
                    url = reverse(name, args={'slug': self.note.slug})
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)
