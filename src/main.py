import logging
import HookEvent

if __name__ == '__main__':
    
    #logging.basicConfig(level=logging.INFO)
    # create logger with 'spam_application'
    
    logger = logging.getLogger('application')
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fhandler = logging.FileHandler('Log.log')
    fhandler.setLevel(logging.INFO)
    # create console handler with a higher log level
    shandler = logging.StreamHandler()
    shandler.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fhandler.setFormatter(formatter)
    shandler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fhandler)
    logger.addHandler(shandler)
    
    #logger.info('instance main')
    hook = HookEvent.HookEvent()
    hook.hookMouseAndKey()

