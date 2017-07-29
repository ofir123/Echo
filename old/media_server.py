import os
import sys
import subprocess

import logbook
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import zmq

# Media server details.
IP = '192.168.10.10'
PORT = '7777'
# Receiver audio constants.
NIRCMD_PATH = r'c:\Program Files\NirCMD\nircmd.exe'
RECEIVER_DEVICE = 'SAMSUNG-4'
COMPUTER_DEVICE = 'Speakers'
# Browser constants.
ADBLOCK_PATH = r'c:\Python35\selenium\webdriver\adblockpluschrome-1.12.1.1627.crx'
# YouTube constants.
YOUTUBE_TEMPLATE = 'https://www.youtube.com/results?search_query='
# Logger constants.
LOGS_DIRECTORY = r'c:\Projects\Echo'
LOG_FILE_NAME = 'media_server.log'

logger = logbook.Logger('MediaServer')


def _get_log_handlers(logs_directory_path=None):
    """
    Returns a list of the nested log handlers setup.
    """
    handlers_list = list()
    handlers_list.append(logbook.NullHandler())
    # Add the rotating file handler, if a logs directory path was supplied.
    if logs_directory_path is not None:
        if not os.path.exists(logs_directory_path):
            os.makedirs(logs_directory_path)
        handlers_list.append(logbook.RotatingFileHandler(os.path.join(logs_directory_path, LOG_FILE_NAME),
                                                         max_size=1024 * 1024, backup_count=5, bubble=True))
    handlers_list.append(logbook.StreamHandler(sys.stdout, level='DEBUG', bubble=True))
    handlers_list.append(logbook.StreamHandler(sys.stderr, level='ERROR', bubble=True))
    return handlers_list


def main():
    """
    Run forever and perform sound card related commands using NirCMD, and browser related commands using Selenium.
    """
    with logbook.NestedSetup(_get_log_handlers(LOGS_DIRECTORY)).applicationbound():
        # Initialize browser options.
        logger.info('Initializing browser and sockets...')
        browser = None
        browser_options = webdriver.ChromeOptions()
        browser_options.add_extension(ADBLOCK_PATH)
        # Initialize server socket.
        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        # Bind to specific IP.
        socket.bind('tcp://*:{}'.format(PORT))
        while True:
            logger.info('Waiting for message...')
            message = socket.recv_string()
            try:
                logger.info('Got {} message!'.format(message))
                if message == 'SOUND_RECEIVER':
                    # Set audio output to receiver.
                    subprocess.check_output('{} setdefaultsounddevice {}'.format(NIRCMD_PATH, RECEIVER_DEVICE))
                    subprocess.check_output('{} setdefaultsounddevice {} 2'.format(NIRCMD_PATH, RECEIVER_DEVICE))
                elif message == 'SOUND_COMPUTER':
                    # Set audio output to computer.
                    subprocess.check_output('{} setdefaultsounddevice {}'.format(NIRCMD_PATH, COMPUTER_DEVICE))
                    subprocess.check_output('{} setdefaultsounddevice {} 2'.format(NIRCMD_PATH, COMPUTER_DEVICE))
                elif message.startswith('YOUTUBE_PLAY_'):
                    # Play YouTube in a dedicated browser.
                    youtube_term = message[13:]
                    if youtube_term:
                        logger.info('Playing {}!'.format(youtube_term))
                        if not browser:
                            browser = webdriver.Chrome(chrome_options=browser_options)
                            window_handles = browser.window_handles
                            if len(window_handles) > 1:
                                # Close the annoying AdBlock tab.
                                browser.switch_to.window(window_handles[1])
                                browser.close()
                                browser.switch_to.window(window_handles[0])
                            browser.maximize_window()
                        browser.get(YOUTUBE_TEMPLATE + youtube_term)
                        # Get all search results.
                        results_list = browser.find_elements_by_class_name(
                            'item-section')[0].find_elements_by_class_name('yt-lockup-content')
                        # Filter out ads and pick the first real result.
                        first_result = None
                        for result in results_list:
                            if len(result.find_elements_by_class_name('yt-badge-ad')) == 0:
                                first_result = result
                                break
                        if first_result:
                            first_result.find_element_by_tag_name('a').click()
                elif message == 'YOUTUBE_PAUSE':
                    if browser:
                        browser.find_element_by_class_name('ytp-play-button').click()
                elif message == 'YOUTUBE_NEXT':
                    if browser:
                        browser.find_element_by_class_name('ytp-next-button').click()
                elif message == 'YOUTUBE_PREVIOUS':
                    if browser:
                        browser.find_element_by_class_name('ytp-prev-button').click()
                elif message == 'YOUTUBE_STOP':
                    # Stop playing YouTube.
                    if browser:
                        browser.quit()
                        browser = None
                elif message.startswith('VIDEO_PLAY_'):
                    # Try and find the video to play.
                    pass
                elif message == 'VIDEO_STOP':
                    # Stop the currently playing video.
                    pass
            except WebDriverException:
                logger.exception('Something bad happened to the browser...')
                # Reset browser object if something went wrong.
                browser = None
            except Exception:
                # Nobody cares... just move on to the next message.
                logger.exception('Something bad happened...')


if __name__ == '__main__':
    # Fix stdout and stderr issues in case of pythonw.
    if sys.executable.endswith("pythonw.exe"):
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
    main()
