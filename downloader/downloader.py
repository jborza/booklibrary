import logging
from apscheduler.schedulers.background import BackgroundScheduler
import urllib.request

def request_cover_download():
    # just get /download_book_covers url
    # TODO use Flask to find out the URL
    urllib.request.urlopen('http://localhost:5000/download_book_covers')
    return

# declared globally, so we can schedule a jobs with decorators
def schedule_cover_download(app):
    # Schedule the download_book_covers function to run every second
    scheduler = BackgroundScheduler()
    scheduler.add_job(func = request_cover_download,
                      trigger='interval',
                      seconds=5, # TODO configure this
                      id='download_book_covers',)
    scheduler.start()
    # Set the logging level for the scheduler to ERROR to avoid too much output
    logging.getLogger('apscheduler.scheduler').setLevel(logging.ERROR)