from application import create_app, rq
from application.utils import qidian_spider, CollaborativeFiltering


@rq.job('spider', timeout=60)
def start_spider(url):
    app = create_app()
    if 'qidian.com' in url:
        qidian_spider(app, url)


@rq.job('cf', timeout=3600)
def run_cf():
    cf = CollaborativeFiltering(create_app())
    cf.save()
    cf.tear_down()