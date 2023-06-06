import pytest
from django.conf import settings
from django.urls import reverse

URL = 'news:home'
DETAIL_URL = 'news:detail'


def test_news_count(client, news_count):
    url = reverse(URL)
    response = client.get(url)
    object_list = response.context['object_list']
    news_count_on_page = len(object_list)
    assert news_count_on_page == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, date_for_news):
    url = reverse(URL)
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, date_for_comments):
    url = reverse(DETAIL_URL, args=[news.id])
    response = client.get(url)
    news = response.context['news']
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, form',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True),
    )
)
def test_pages_contains_form(news, parametrized_client, form):
    url = reverse(DETAIL_URL, args=[news.id])
    response = parametrized_client.get(url, args=[news.id])
    context = response.context
    assert ('form' in context) == form
