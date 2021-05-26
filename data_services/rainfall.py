import os
import logging
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO)
logging.captureWarnings(True)


class RAINFALL:
    def __init__(self):
        self.daily_total = 0.0
        self.scheduler = BackgroundScheduler()

        # Setup scheduled reset of daily rain amount, uses the system time
        self.scheduler.add_job(self.reset_total, CronTrigger(
            hour=int(os.getenv('RAINFALL_RESET', '9')), minute=0))
        self.scheduler.start()

    def reset_total(self):
        logging.info('Resetting daily rain total to zero')
        self.daily_total = 0.0

    # def data_update(self, tip_amount):
    #     self.daily_total = self.daily_total + float(tip_amount)

    def get_total(self, tip_amount):
        """
        Get the latest instrument readings.
        :return: Current total rainfall (same units tip amount).
        """
        self.daily_total = self.daily_total + float(tip_amount)
        return round(self.daily_total, 1)
