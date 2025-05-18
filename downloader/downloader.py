import logging
from apscheduler.schedulers.background import BackgroundScheduler
import urllib.request

def download_book_covers():
    # just get /download_book_covers url
    urllib.request.urlopen('http://localhost:5000/download_book_covers')
    return

# declared globally, so we can schedule a jobs with decorators
def schedule_cover_download(app):
    # Schedule the download_book_covers function to run every second
    scheduler = BackgroundScheduler()
    scheduler.add_job(func = download_book_covers,
                      trigger='interval',
                      seconds=1,
                      id='download_book_covers',)
    scheduler.start()
    # Set the logging level for the scheduler to ERROR to avoid too much output
    logging.getLogger('apscheduler.scheduler').setLevel(logging.ERROR)