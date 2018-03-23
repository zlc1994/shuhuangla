from application import create_app
from application.main.tasks import start_spider, run_cf

app = create_app()

with app.app_context():

    run_cf.queue()