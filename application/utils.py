import requests
from application import db
from bs4 import BeautifulSoup
import re
import json
import arrow
import csv
from application.models import Comment, Book
from application import r


class CollaborativeFiltering(object):
    def __init__(self, app):
        self.book_data = {}
        self.user_data = {}
        self.app = app

        self.load()

    def load(self):
        # load from db
        with self.app.app_context():
            for comment in Comment.query.all():
                self.book_data.setdefault(comment.book.book_id, {})
                self.user_data.setdefault(comment.user_id, {'total': 0, 'count': 0})
                self.book_data[comment.book.book_id][comment.user_id] = comment.score
                self.user_data[comment.user_id]['total'] += comment.score
                self.user_data[comment.user_id]['count'] += 1

        # load from csv

        with open(self.app.config['CSV'], 'r',  newline='') as f:
            fieldnames = ['user_id', 'book_id', 'rate']
            reader = csv.DictReader(f, fieldnames=fieldnames)
            next(reader, None)  # skip the headers
            for row in reader:
                self.book_data.setdefault(row['book_id'], {})
                self.user_data.setdefault(row['user_id'], {'total': 0, 'count': 0})
                self.book_data[row['book_id']][row['user_id']] = int(row['rate'])
                self.user_data[row['user_id']]['total'] += int(row['rate'])
                self.user_data[row['user_id']]['count'] += 1

    def similarity(self, u, v):
        common = {}

        for user in self.book_data[u]:
            if user in self.book_data[v]:
                common[user] = 1

        l = len(common)

        if not l:
            return 0
        elif l > 50:
            factor = 1
        else:
            factor = l / 50

        len_u = sum([(self.book_data[u][i] - self.user_data[i]['total'] / self.user_data[i]['count']) ** 2 for i in common]) ** 0.5
        len_v = sum([(self.book_data[v][i] - self.user_data[i]['total'] / self.user_data[i]['count']) ** 2 for i in common]) ** 0.5

        den = len_u * len_v

        if not den:
            return 0

        dot = 0
        for i in common:
            bias = self.user_data[i]['total'] / self.user_data[i]['count']
            dot += (self.book_data[u][i] - bias) * (self.book_data[v][i] - bias)

        return factor * dot / den

    def top_matches(self, book_id, top_n=20):
        res = []

        for book in self.book_data:
            if book != book_id:
                res.append((self.similarity(book, book_id), book))

        res.sort()
        res.reverse()

        return res[:top_n]

    def save(self):
        with self.app.app_context():
            r.flushdb()
            for book in Book.query.all():
                if book.book_id not in self.book_data:
                    continue
                for si, si_book in self.top_matches(book.book_id):
                    b = Book.query.filter(Book.book_id == si_book).first()
                    if b:
                        r.hmset(book.id, {b.id: si})



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

    pc_url = 'http://book.qidian.com/info/{}#Catalog'.format(book_id)

    with app.app_context():
        book = Book.query.filter_by(pc_url=pc_url).first()

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
                pc_url=pc_url,
                m_url=url
            )
            db.session.add(book)
        db.session.commit()

