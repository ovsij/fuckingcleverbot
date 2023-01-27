from aiogram.utils import executor
import logging

from bot import dp

if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception:
            logging.exception('polling error')
    




