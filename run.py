from time import sleep
from os import listdir
from importlib import import_module
import pychromecast
import logging
import argparse


def setup_connection(name):
    """ Look for available devices and ask the user which one he wants to connect to """
    # Scan for all available Chromecasts
    print("Scanning for all available chromecasts ...\n")
    chromecasts = pychromecast.get_chromecasts()
    chromecast = None

    if name is not None:
        for cc in chromecasts:
            if cc.device.friendly_name.lower() == name.lower():
                chromecast = cc
                break

        if chromecast is None:
            print("A chromecast named {} couldn't be found. Let's check for others.", name)

    if chromecast is None:
        chromecasts = sorted(chromecasts, key=lambda cast: cast.device.friendly_name)
        count_ccs = len(chromecasts)
        # List them if there are any, else quit
        if count_ccs == 0:
            print("Done scanning. No chromecasts found at all. Exiting ..")
            raise SystemExit
        else:
            print("Done scanning. Here are the results:")
            for i, cc in enumerate(chromecasts):
                print("{}: {}{}".format(i, cc.device.friendly_name, "\n" if i == count_ccs - 1 else ""))
        # Let the user choose the one he wants to connect to
        chromecast = None
        while chromecast is None:
            try:
                val = int(input("Choose the one you're interested in: "))
                if not 0 <= val <= count_ccs - 1:
                    raise ValueError('out of range')
                chromecast = chromecasts[val]
            except ValueError:
                print("Enter a number between 0 and {}".format(count_ccs - 1))

    # Connect to the chosen one
    print("Connecting to {} ...\n".format(chromecast.device.friendly_name))
    chromecast.wait()
    print("Connected!\n")
    return chromecast.media_controller


def get_image_source(name):
    """ Asking the user which image-source he wants to use """
    # Get the image source
    pages = listdir("pages")
    pages = [page for page in pages if (page.endswith(".py") and page != "__init__.py")]
    source = None

    if name is not None:
        for page in pages:
            if page[:-3].lower() == name.lower():
                source = import_module("{}.{}".format("pages", name))
                break

        if source is None:
            print("A source named {} couldn't be found. Let's check for others.", name)

    if source is None:
        print("Now please choose the source where the images should come from:")
        pages.sort()
        for i, page in enumerate(pages):
            print("{}: {}{}".format(i, page[:-3], "\n" if i == len(pages) - 1 else ""))
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
    if args.info is True:
        print("=====")
        if image.author is not None:
            print("Author:\t{}".format(image.author))
        if image.title is not None:
            print("Title:\t{}".format(image.title))
        print("Url:\t{}".format(image.url))

    sleep(sleep_time)
    src.get_next_image(on_image_received)


def set_log_levels():
    logging.getLogger('scrapy').propagate = False
    logging.getLogger('pychromecast').propagate = False


def setup_argparser():
    def check_positive(x):
        err = argparse.ArgumentTypeError("Value must be a number >= 1")
        try:
            x = int(x)
        except ValueError:
            raise err
        if x < 1:
            raise err
        return x

    parser = argparse.ArgumentParser("drimcast - cast images automatically to your chromecast and enjoy.")
    parser.add_argument("-cc", "--chromecast",
                        help="the chromecast to cast to",
                        dest="chromecast",
                        metavar="name")
    parser.add_argument("-src", "--source",
                        help="the image source to use",
                        dest="source",
                        metavar="name")
    parser.add_argument("-d", "--duration",
                        help="amount of time an image should be shown in seconds >= 1",
                        dest="duration",
                        metavar="amount",
                        type=check_positive)
    parser.add_argument("-i", "--info",
                        help="show image related info such as title, author and link. true if arg is given, else false",
                        dest="info",
                        action="store_true")
    return parser.parse_args()


set_log_levels()
args = setup_argparser()
mc = setup_connection(args.chromecast)
src = get_image_source(args.source)
sleep_time = args.duration or get_sleep_time()

# get and show first image..
src.get_next_image(on_image_received)

# keep alive
input("Press enter to exit.")
