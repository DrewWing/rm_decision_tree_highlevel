

# Some tests for decision trees for Sentry.

import logging

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(filename='app.log', level=logging.INFO)
    logger.info("Program start")

if __name__ == '__main__':
    main()

