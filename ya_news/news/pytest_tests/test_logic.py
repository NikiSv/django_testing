from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError

DETAIL_URL = 'news:detail'
EDIT_URL = 'news:edit'
DELETE_URL = 'news:delete'


def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse(DETAIL_URL, args=[news.id])
    response = client.post(url, data=form_data)
    assert response.status_code == 302
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author_client, author, form_data, news):
    url = reverse(DETAIL_URL, args=[news.id])
    response = author_client.post(url, data=form_data)
    expected_url = reverse(DETAIL_URL, args=[news.id]) + '#comments'
    assert response.url == expected_url
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, bad_word, news):
    url = reverse(DETAIL_URL, args=[news.pk])
    bad_words_data = {'text': bad_word}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(author_client, form_data, news, comments,
                                 pk_for_args):
    url = reverse(EDIT_URL, args=pk_for_args)
    response = author_client.post(url, form_data)
    expected_url = reverse(DETAIL_URL, args=[news.pk]) + '#comments'
    assert response.url == expected_url
    comments.refresh_from_db()
    assert comments.text == form_data['text']


def test_author_can_delete_comment(author_client, news, pk_for_args):
    url = reverse(DELETE_URL, args=pk_for_args)
    response = author_client.post(url)
    expected_url = reverse(DETAIL_URL, args=[news.pk]) + '#comments'
    assert response.url == expected_url
    assert Comment.objects.count() == 0


def test_user_cant_edit_comment_of_another_user(reader_client,
                                                form_data, comments,
                                                pk_for_args):
    url = reverse(EDIT_URL, args=pk_for_args)
    response = reader_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comments.id)
    assert comments.news == comment_from_db.news
    assert comments.text == comment_from_db.text
    assert comments.author == comment_from_db.author


def test_user_cant_delete_comment_of_another_user(reader_client, pk_for_args):
    url = reverse(DELETE_URL, args=pk_for_args)
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
