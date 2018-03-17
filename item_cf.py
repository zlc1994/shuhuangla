import csv
from application.models import Comment, Book
from application import r


class CollaborativeFiltering(object):
    def __init__(self, csv_file='comments.csv'):
        self.book_data = {}
        self.user_data = {}
        self.csv_file = csv_file
        self.load()

    def load(self):
        # load from db
        for comment in Comment.query.all():
            self.book_data.setdefault(comment.book.book_id, {})
            self.user_data.setdefault(comment.user_id, {'total': 0, 'count': 0})
            self.book_data[comment.book.book_id][comment.user_id] = comment.score
            self.user_data[comment.user_id]['total'] += comment.score
            self.user_data[comment.user_id]['count'] += 1

        # load from csv

        with open(self.csv_file, 'r',  newline='') as f:
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
        r.flushdb()
        for book in Book.query.all():
            if book.book_id not in self.book_data:
                continue
            for si, si_book in self.top_matches(book.book_id):
                b = Book.query.filter(Book.book_id == si_book).first()
                if b:
                    r.hmset(book.id, {b.id: si})


if __name__ == "__main__":
    cf = CollaborativeFiltering()
    cf.save()





