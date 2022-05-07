import sys
import os
from typing import Callable
from functools import partial
from src.adb import retrieve_images_from_phone, retrieve_videos_from_phone
from src.ffmpeg import generate_background_images
from src.image import extract_objects, resize_background_image, generate_training_image, cleanup


class Proc(object):
    def __init__(self, name: str, func: Callable[[str], None]):
        self.__name = name
        self.__func = func

    @property
    def name(self) -> str:
        return self.__name

    @property
    def func(self) -> Callable[[str], None]:
        return self.__func


if __name__ == "__main__":
    root_path = os.path.dirname(os.path.realpath(__file__))

    procs = []
    procs.append(Proc('Retrieve images from android mobile phone', retrieve_images_from_phone))
    procs.append(Proc('Retrieve videos from android mobile phone', retrieve_videos_from_phone))
    procs.append(Proc('Convert video to images', generate_background_images))
    procs.append(Proc('Resize background image', resize_background_image))
    procs.append(Proc('Extract objects', extract_objects))
    procs.append(Proc('Generate training image', partial(generate_training_image, output_folder_prefix = 'training')))
    procs.append(Proc('Generate validation image', partial(generate_training_image, output_folder_prefix = 'validation')))
    procs.append(Proc('Generate test image', partial(generate_training_image, output_folder_prefix = 'test')))
    procs.append(Proc('Clean up training, validation and test images', cleanup))

    print('Select:')
    for index, proc in enumerate(procs):
        print('{0}. {1}'.format(index + 1, proc.name))

    selection = int(input())
    if selection > len(procs) or selection < 1:
        print('Error: selection out of range!')
        sys.exit(-1)

    procs[selection - 1].func(root_path)

    print('Done')

