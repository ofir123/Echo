import subprocess
from functools import wraps

import logbook
import ujson
from flask import Blueprint, make_response
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException, ElementNotVisibleException

from . import config

app_views = Blueprint('app_views', __name__)

logger = logbook.Logger(__name__)

shared_browser = None


def _make_error_response(error_string):
    """
    Return an error response to the user.

    :param error_string: The error string to write.
    :return: The server error response.
    """
    logger.error(error_string)
    return make_response(ujson.dumps({'error': error_string}))


def selenium_wrapper(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        global shared_browser

        if not shared_browser:
            # Initialize browser options.
            logger.info('Initializing browser and sockets...')
            browser_options = webdriver.ChromeOptions()
            browser_options.add_extension(config.ADBLOCK_PATH)
            shared_browser = webdriver.Chrome(chrome_options=browser_options)
            window_handles = shared_browser.window_handles
            if len(window_handles) > 1:
                # Close the annoying AdBlock tab.
                shared_browser.switch_to.window(window_handles[1])
                shared_browser.close()
                shared_browser.switch_to.window(window_handles[0])
            shared_browser.maximize_window()

        kwargs['browser'] = shared_browser
        try:
            view(*args, **kwargs)
        except (NoSuchElementException, ElementNotVisibleException):
            logger.exception('Element wasn\'t found in the browser...')
        except WebDriverException:
            logger.exception('Something bad happened to the browser...')
            # Reset browser object if something went wrong.
            try:
                shared_browser.quit()
            except WebDriverException:
                pass
            shared_browser = None
        return ''

    return decorated


@app_views.route('/audio/receiver', methods=['GET'])
def set_audio_receiver():
    # Set audio output to receiver.
    logger.info('Setting audio device to receiver')
    subprocess.check_output('{} setdefaultsounddevice {}'.format(config.NIRCMD_PATH, config.RECEIVER_DEVICE))
    subprocess.check_output('{} setdefaultsounddevice {} 2'.format(config.NIRCMD_PATH, config.RECEIVER_DEVICE))
    return ''


@app_views.route('/audio/computer', methods=['GET'])
def set_audio_computer():
    # Set audio output to computer.
    logger.info('Setting audio device to computer')
    subprocess.check_output('{} setdefaultsounddevice {}'.format(config.NIRCMD_PATH, config.COMPUTER_DEVICE))
    subprocess.check_output('{} setdefaultsounddevice {} 2'.format(config.NIRCMD_PATH, config.COMPUTER_DEVICE))
    return ''


@app_views.route('/youtube/play/<term>', methods=['GET'])
@selenium_wrapper
def youtube_play(term, browser):
    if not term:
        _make_error_response('Must supply a term for YouTube to play')
    logger.info('Playing {} on YouTube!'.format(term))
    # Set browser URL.
    browser.get(config.YOUTUBE_TEMPLATE + term)
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


@app_views.route('/youtube/resume', methods=['GET'])
@selenium_wrapper
def youtube_resume(browser):
    logger.info('Resuming YouTube video')
    browser.find_element_by_class_name('ytp-play-button').click()


@app_views.route('/youtube/pause', methods=['GET'])
@selenium_wrapper
def youtube_pause(browser):
    logger.info('Pausing YouTube video')
    browser.find_element_by_class_name('ytp-play-button').click()


@app_views.route('/youtube/next', methods=['GET'])
@selenium_wrapper
def youtube_next(browser):
    logger.info('Playing the next video on YouTube')
    browser.find_element_by_class_name('ytp-next-button').click()


@app_views.route('/youtube/stop', methods=['GET'])
def youtube_stop():
    global shared_browser

    logger.info('Stopping YouTube')
    try:
        shared_browser.quit()
    except WebDriverException:
        pass
    shared_browser = None
    return ''
