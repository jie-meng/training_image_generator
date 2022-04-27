import os
import sys
import re
import random
import subprocess
from typing import Tuple
from src.model import CategoryItems, TrainingItemInfo, CompositeImageInfo
from src.xml import generate_xml
from src.utils import is_intersection

def get_width_height(image) -> Tuple[int]:
    result = subprocess.getoutput('identify -ping -format "%w %h" {0}'.format(image))
    width_height = result.split(' ')
    return (int(width_height[0]), int(width_height[1]))

def extract_objects(root_path: str):
    object_categories = list(filter(lambda x: os.path.isdir(root_path + '/generated/object/' + x), os.listdir(root_path + '/generated/object')))

    percent = input('What is the resize ratio of the objects? (default: 100%)\n')
    if not re.match('\d+%?', percent):
        print('Error: percent format incorrect')
        sys.exit(-1)

    percent = percent.replace('%', '')

    for index, category in enumerate(object_categories):
        images = list(filter(lambda x: '{0}/generated/object/{1}/{2}'.format(root_path, category, x).endswith('jpg'), os.listdir('{0}/generated/object/{1}'.format(root_path, category))))
        if len(images) > 0:
            target_folder = '{0}/generated/extracted_object/{1}'.format(root_path, category)
            if not os.path.isdir(target_folder):
                os.mkdir(target_folder)

            for image in images:
                basename = os.path.splitext(image)[0]
                target_image = '{0}/generated/extracted_object/{1}/{2}.png'.format(root_path, category, basename)

                if os.path.isfile(target_image):
                    continue

                os.system('backgroundremover -i "{0}/generated/object/{1}/{2}" -a -ae 15 -o "{3}"'.format(root_path, category, image, target_image))
                os.system('convert {0} -trim -resize {1}% +repage {0}'.format(target_image, percent))

def generate_training_image(root_path: str):
    # clean up
    os.system('rm {0}/generated/training_image/*.png'.format(root_path))
    os.system('rm {0}/generated/training_image_with_item_border/*.png'.format(root_path))
    os.system('rm {0}/generated/training_image_info/*.xml'.format(root_path))

    object_categories = list(filter(lambda x: os.path.isdir(root_path + '/generated/extracted_object/' + x), os.listdir(root_path + '/generated/extracted_object')))
    backgrounds = list(filter(lambda x: '{0}/generated/background/image/{1}'.format(root_path, x).endswith('jpg'), os.listdir(root_path + '/generated/background/image')))

    print('Please input what objects should be generated into training images? (e.g. 1,2,3)')
    for index, item in enumerate(object_categories):
        print('{0}. {1}'.format(index + 1, item))

    content = input()
    is_match = re.match('[\d,]+', content)
    if not is_match:
        print('Error: Format incorrect!')
        sys.exit(-1)

    select_categories = content.split(',')
    select_categories = list(map(lambda y: int(y), filter(lambda x: re.match('\d+', x) and int(x) <= len(object_categories) and int(x) > 0, select_categories)))

    category_items_list = []
    for index in select_categories:
        category = object_categories[index - 1]
        category_items_list.append(CategoryItems(category, list(filter(lambda x: x.endswith('png'), os.listdir('{0}/generated/extracted_object/{1}'.format(root_path, category))))))

    genrerate_count = int(input('How many training images to be generated?\n'))
    if genrerate_count < 1:
        print('Error: generate count should not less than 1!')
        sys.exit(-1)

    existing_training_images = list(filter(lambda x: x.endswith('png'), os.listdir('{0}/generated/training_image'.format(root_path))))

    for index in range(0, genrerate_count):
        # random backgrounds
        random_background = backgrounds[random.randint(0, len(backgrounds) - 1)]
        bk_wh = get_width_height('{0}/generated/background/image/{1}'.format(root_path, random_background))

        # gnerate training items
        training_items = []
        for category_items in category_items_list:
            random_item = category_items.items[random.randint(0, len(category_items.items) - 1)]
            training_item_info = TrainingItemInfo(category_items.category, random_item)
            item_wh = get_width_height('{0}/generated/extracted_object/{1}/{2}'.format(root_path, training_item_info.category, training_item_info.name))
            training_item_info.width = item_wh[0]
            training_item_info.height = item_wh[1]
            training_item_info.position = (random.randint(0, bk_wh[0] - item_wh[0]), random.randint(0, bk_wh[1] - item_wh[1]))

            training_items.append(training_item_info)

        random.shuffle(training_items)

        # check truncate
        #  for i, x in enumerate(training_items):
        #      if i < len(training_items) - 1:
        #          for y in training_items[i + 1:]:
        #              is_truncated = is_intersection(x.position[0], x.position[0] + x.width, x.position[1], x.position[1] + x.height,
        #                              y.position[0], y.position[0] + y.width, y.position[1], y.position[1] + y.height)
        #              if is_truncated:
        #                  x.is_truncated = is_truncated
        #                  break

        generate_cmd = 'convert {0}/generated/background/image/{1}'.format(root_path, random_background)
        for item in training_items:
            generate_cmd += ' {0}/generated/extracted_object/{1}/{2} -geometry +{3}+{4} -composite'.format(root_path, item.category, item.name, item.position[0], item.position[1])

        dest_image = '{0}/generated/training_image/image{1}.png'.format(root_path, len(existing_training_images) + index + 1)
        generate_cmd += ' {0}'.format(dest_image)
        print(generate_cmd)
        os.system(generate_cmd)

        border_image_cmd = 'convert {0}/generated/training_image/image{1}.png -fill none -stroke yellow -strokewidth 2 -draw "'.format(root_path, len(existing_training_images) + index + 1)
        for item in training_items:
            border_image_cmd += 'rectangle {0},{1} {2},{3} '.format(item.position[0], item.position[1], item.position[0] + item.width, item.position[1] + item.height)

        dest_image_with_border = '{0}/generated/training_image_with_item_border/image{1}.png'.format(root_path, len(existing_training_images) + index + 1)
        border_image_cmd += '" {0}'.format(dest_image_with_border)
        print(border_image_cmd)
        os.system(border_image_cmd)

        generate_xml(root_path, CompositeImageInfo(dest_image, bk_wh[0], bk_wh[1], training_items))

