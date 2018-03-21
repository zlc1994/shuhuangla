import requests
from application import db, rq, create_app
from bs4 import BeautifulSoup
from application.models import Book
import arrow
import re


def qidian_spider(app, url):
    if '#Catalog' not in url:
        url = url + '#Catalog'
    url = url.replace('https://', 'http://')

    # extract book detail
    r = requests.get(url)
    if r.status_code != 200:
        return

    soup = BeautifulSoup(r.text, 'lxml')

    cover = soup.find('div', class_='book-img').a.img.get('src')
    info_field = soup.find('div', class_='book-info')
    bookname = info_field.h1.em.text
    author = info_field.span.a.text
    tag = info_field.find('p', class_='tag').a.text
    intro = soup.find('div', class_='book-intro').text
    chapters = soup.find('div', class_='volume-wrap').find_all('li')
    total_chapters = len(chapters)
    total_words = 0
    last_update = arrow.get(chapters[-1].a.get('title'), 'YYYY-MM-DD HH:mm:ss').replace(tzinfo='Asia/Shanghai')
    last_chapter = chapters[-1].a.text

    # count total words
    for c in chapters:
        title = c.a.get('title')
        words = re.search('章节字数：(\d+)', title)
        if words:
            total_words += int(words.group(1))

    with app.app_context():
        book = Book.query.filter_by(pc_url=url).first()

        if book:
            book.cover = cover
            book.chapters = total_chapters
            book.words = total_words
            book.last_update = last_update
            book.tag = tag
        else:
            book = Book(
                bookname=bookname,
                author=author,
                tag=tag,
                intro=intro,
                chapters=total_chapters,
                words=total_words,
                last_update=last_update,
                last_chapter=last_chapter,
                cover=cover,
                source='起点中文网',
                pc_url=url,
            )
            db.session.add(book)
        db.session.commit()


@rq.job(timeout=60)
def start_spider(url):
    if 'qidian.com' in url:
        qidian_spider(create_app(), url)

