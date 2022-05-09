import os
import sys
import subprocess
from src.utils import get_object_categories

def retrieve_images_from_phone(root_path: str):
    result = subprocess.getoutput('adb shell ls /sdcard/DCIM/Camera')
    items = result.split('\n')
    items.sort(reverse = True)
    items = list(filter(lambda x: x.endswith('jpg') and x.startswith('IMG'), items))

    print('What is the category of the object?')
    object_categories = get_object_categories(root_path)
    for index, item in enumerate(object_categories):
        print('{0}. {1}'.format(index + 1, item))

    selection = int(input())
    if selection > len(object_categories) or selection < 1:
        print('Error: selection out of range!')
        sys.exit(-1)

    category = object_categories[selection - 1]

    existed_images = list(filter(lambda x: os.path.isfile('{0}/generated/object/{1}/{2}'.format(root_path, category, x)) and x.endswith('jpg'), os.listdir('{0}/generated/object/{1}'.format(root_path, category))))
    existed_images_count = len(existed_images)

    count = int(input('How many images to retrieve (latest)?\n'))
    images = items[:count]

    for index, image in enumerate(images):
        os.system('adb pull /sdcard/DCIM/Camera/{0} {1}/generated/object/{2}/{2}_{3}.jpg'.format(image, root_path, category, index + existed_images_count + 1))


def retrieve_videos_from_phone(root_path: str):
    result = subprocess.getoutput('adb shell ls /sdcard/DCIM/Camera')
    items = result.split('\n')
    items.sort(reverse = True)
    items = list(filter(lambda x: x.endswith('mp4') and x.startswith('VID'), items))

    existed_backgrounds = list(filter(lambda x: os.path.isfile('{0}/generated/background/video/{1}'.format(root_path, x)) and x.endswith('mp4'), os.listdir('{0}/generated/background/video'.format(root_path))))
    existed_background_count = len(existed_backgrounds)

    count = int(input('How many videos to retrieve (latest)?\n'))
    videos = items[:count]

    for index, video in enumerate(videos):
        os.system('adb pull /sdcard/DCIM/Camera/{0} {1}/generated/background/video/background_{2}.mp4'.format(video, root_path, index + existed_background_count + 1))

def retrieve_check_images_from_phone(root_path: str):
    result = subprocess.getoutput('adb shell ls /sdcard/DCIM/Camera')
    items = result.split('\n')
    items.sort(reverse = True)
    items = list(filter(lambda x: x.endswith('jpg') and x.startswith('IMG'), items))

    existed_images = list(filter(lambda x: os.path.isfile('{0}/generated/check_image/{1}'.format(root_path, x)) and x.endswith('jpg'), os.listdir('{0}/generated/check_image'.format(root_path))))
    existed_images_count = len(existed_images)

    count = int(input('How many images to retrieve (latest)?\n'))
    images = items[:count]

    for index, image in enumerate(images):
        os.system('adb pull /sdcard/DCIM/Camera/{0} {1}/generated/check_image/image_{2}.jpg'.format(image, root_path, index + existed_images_count + 1))
