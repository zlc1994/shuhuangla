import requests
from application import db, rq, create_app
from bs4 import BeautifulSoup
from application.models import Book
import arrow
import re
import json


def qidian_spider(app, url):
    book_id = re.search('\d+', url)
    if book_id is None:
        return
    book_id = book_id.group(0)

    # crawl the mobile page
    url = 'https://m.qidian.com/book/' + book_id

    # extract book detail
    r = requests.get(url)
    if r.status_code != 200:
        return

    soup = BeautifulSoup(r.text, 'lxml')

    cover = soup.find('div', class_='book-layout').img.get('src')
    bookname = soup.find('h2', class_='book-title').text
    author = soup.find('h4', class_='book-title').text
    tag = soup.find('p', class_='book-meta').text
    intro = soup.find('content').text

    # use api to get chapter details
    r = requests.get('https://book.qidian.com/ajax/book/category?bookId='+book_id)
    r.encoding  = 'utf-8'
    results = json.loads(r.text)

    if results['code']:
        return

    total_chapters = results['data']['chapterTotalCnt']
    total_words = 0
    last_update = arrow.get(results['data']['vs'][-1]['cs'][-1]['uT'],
                            'YYYY-MM-DD HH:mm:ss').replace(tzinfo='Asia/Shanghai')
    last_chapter = results['data']['vs'][-1]['cs'][-1]['cN']

    # count total words
    for volume in results['data']['vs']:
        for c in volume['cs']:
            total_words += c['cnt']

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

