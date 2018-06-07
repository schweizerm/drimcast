from time import sleep
from os import listdir
from importlib import import_module
import pychromecast
import logging


def setup_connection():
    """ Look for available devices and ask the user which one he wants to connect to """
    # Scan for all available Chromecasts
    print("Scanning for all available chromecasts ...\n")
    chromecasts = pychromecast.get_chromecasts()
    chromecasts = sorted(chromecasts, key=lambda cast: cast.device.friendly_name)
    count_ccs = len(chromecasts)
    print("Done scanning. Here are the results:")
    # List them if there are any, else quit
    if count_ccs == 0:
        print("No chromecasts found. Exiting ..")
        raise SystemExit
    else:
        for i, cc in enumerate(chromecasts):
            print("{}: {}{}".format(i, cc.device.friendly_name, "\n" if i == count_ccs - 1 else ""))
    # Let the user choose the one he wants to connect to
    cc = None
    while cc is None:
        try:
            val = int(input("Choose the one you're interested in: "))
            if not 0 <= val <= count_ccs - 1:
                raise ValueError('out of range')
            cc = chromecasts[val]
        except ValueError:
            print("Enter a number between 0 and {}".format(count_ccs - 1))
    # Connect to the chosen one
    print("Connecting to {} ...\n".format(cc.device.friendly_name))
    cc.wait()
    print("Connected!\n")
    return cc.media_controller


def get_image_source():
    """ Asking the user which image-source he wants to use """
    # Get the image source
    print("Now please choose the source where the images should come from:")
    pages = listdir("pages")
    pages = [page for page in pages if (page.endswith(".py") and page != "__init__.py")]
    for i, page in enumerate(pages):
        print("{}: {}{}".format(i, page[:-3], "\n" if i == len(pages) - 1 else ""))
    source = None
    while source is None:
        try:
            val = int(input("Choose the one you're interested in: "))
            if not 0 <= val <= len(pages) - 1:
                raise ValueError('out of range')
            source = import_module("{}.{}".format("pages", (pages[val])[:-3]))
        except ValueError:
            print("Enter a number between 0 and {}".format(len(pages) - 1))

    return source


def get_sleep_time():
    """ Asking the user how long an image should be shown """
    # For how long should a single image stay?
    time = None
    while time is None:
        try:
            val = int(input("Please enter the amount of seconds for a picture to stay: "))
            if not val > 0:
                raise ValueError('value must be greater than 0')

            time = val
        except ValueError:
            pass

    return time


def on_image_received(image):
    """ Images might not be crawled yet, which may take a while. As soon as we have an image this method is called"""
    global src
    mc.play_media(image.url, image.mime_type, image.title, image.url)
    if not mc.is_active:
        mc.block_until_active()
    sleep(sleep_time)
    src.get_next_image(on_image_received)


def set_log_levels():
    logging.getLogger('scrapy').propagate = False
    logging.getLogger('pychromecast').propagate = False


set_log_levels()
mc = setup_connection()
src = get_image_source()
sleep_time = get_sleep_time()

# get and show first image..
src.get_next_image(on_image_received)

# keep alive
input("Press enter to exit.")
