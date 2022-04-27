import os
import sys
import re

def generate_background_images(root_path: str):
    existed_backgrounds = list(filter(lambda x: os.path.isfile('{0}/generated/background/video/{1}'.format(root_path, x)) and x.endswith('mp4'), os.listdir('{0}/generated/background/video'.format(root_path))))
    print(existed_backgrounds)

    print('Select source background:')
    for index, item in enumerate(existed_backgrounds):
        print('{0}. {1}'.format(index + 1, item))

    selection = int(input())
    if selection > len(existed_backgrounds) or selection < 1:
        print('Error: selection out of range!')
        sys.exit(-1)

    video = existed_backgrounds[selection - 1]

    existed_background_images = list(filter(lambda x: os.path.isfile('{0}/generated/background/image/{1}'.format(root_path, x)) and x.endswith('jpg'), os.listdir('{0}/generated/background/image'.format(root_path))))

    crop = input('Please input crop size: (width:height:x:y)\n')
    is_match = re.match('\d+:\d+:\d+:\d+', crop)
    if not is_match:
        print('Error: crop format should be width:height:x:y')
        sys.exit(-1)

    os.system('ffmpeg -i "{0}/generated/background/video/{1}" -vf fps="2",crop="{3}" -qscale:v 2 -start_number "{2}" "{0}/generated/background/image/background_%d.jpg"'.format(root_path, video, len(existed_background_images) + 1, crop))

