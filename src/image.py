import os
import sys
import re
import random
import subprocess
from typing import Tuple, List
from src.xml import generate_xml
from src.utils import is_intersection, get_object_categories, get_extracted_object_categories, CategoryItems, TrainingItemInfo, CompositeImageInfo

def get_width_height(image) -> Tuple[int]:
    result = subprocess.getoutput('identify -ping -format "%w %h" {0}'.format(image))
    width_height = result.split(' ')
    return (int(width_height[0]), int(width_height[1]))

def extract_objects(root_path: str):
    object_categories = get_object_categories(root_path)

    percent = input('What is the resize ratio of the objects? (default: 100%)\n')
    if not re.match('\d+%?', percent):
        print('Error: ratio format incorrect')
        sys.exit(-1)

    percent = percent.replace('%', '')

    for index, category in enumerate(object_categories):
        images = list(filter(lambda x: '{0}/generated/object/{1}/{2}'.format(root_path, category, x).endswith('.jpg'), os.listdir('{0}/generated/object/{1}'.format(root_path, category))))
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

def resize_background_image(root_path: str):
    background_images = list(filter(lambda x: x.endswith('.jpg'), os.listdir(root_path + '/generated/background/image')))

    percent = input('What is the resize ratio of the objects? (default: 100%)\n')
    if not re.match('\d+%?', percent):
        print('Error: ratio format incorrect')
        sys.exit(-1)

    for image in background_images:
        cmd = 'convert {0}/generated/background/image/{1} -resize {2}% {0}/generated/background/image/{1}'.format(root_path, image, percent)
        print(cmd)
        os.system(cmd)

def generate_one_image(
    root_path: str,
    backgrounds: List[str],
    category_items_list: List[CategoryItems],
    output_folder_prefix: str
    ):
    existing_training_images = list(filter(lambda x: x.endswith('.jpg'), os.listdir('{0}/generated/{1}_image'.format(root_path, output_folder_prefix))))

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

    #  check covered
    for i, x in enumerate(training_items):
        if i < len(training_items) - 1:
            for y in training_items[i + 1:]:
                is_covered = is_intersection(x.position[0], x.position[0] + x.width, x.position[1], x.position[1] + x.height,
                                y.position[0], y.position[0] + y.width, y.position[1], y.position[1] + y.height)
                if is_covered:
                    x.is_covered = is_covered
                    break

    generate_cmd = 'convert {0}/generated/background/image/{1}'.format(root_path, random_background)
    for item in training_items:
        generate_cmd += ' {0}/generated/extracted_object/{1}/{2} -geometry +{3}+{4} -composite'.format(root_path, item.category, item.name, item.position[0], item.position[1])

    dest_image = '{0}/generated/{2}_image/image{1}.jpg'.format(root_path, len(existing_training_images) + 1, output_folder_prefix)
    generate_cmd += ' {0}'.format(dest_image)
    print(generate_cmd)
    os.system(generate_cmd)

    border_image_cmd = 'convert {0}/generated/{2}_image/image{1}.jpg -fill none -stroke yellow -strokewidth 2 -draw "'.format(root_path, len(existing_training_images) + 1, output_folder_prefix)
    for item in training_items:
        border_image_cmd += 'rectangle {0},{1} {2},{3} '.format(item.position[0], item.position[1], item.position[0] + item.width, item.position[1] + item.height)

    dest_image_with_border = '{0}/generated/{2}_image_with_item_border/image{1}.jpg'.format(root_path, len(existing_training_images) + 1, output_folder_prefix)
    border_image_cmd += '" {0}'.format(dest_image_with_border)
    print(border_image_cmd)
    os.system(border_image_cmd)

    generate_xml(root_path, CompositeImageInfo(dest_image, bk_wh[0], bk_wh[1], training_items), output_folder_prefix)


def generate_training_image(root_path: str, output_folder_prefix: str):
    object_categories = get_extracted_object_categories(root_path)
    backgrounds = list(filter(lambda x: '{0}/generated/background/image/{1}'.format(root_path, x).endswith('jpg'), os.listdir(root_path + '/generated/background/image')))

    # print('Please input what objects should be generated into training images? (e.g. 1,2,3)')
    # for index, item in enumerate(object_categories):
    #     print('{0}. {1}'.format(index + 1, item))

    # content = input()
    # is_match = re.match('[\d,]+', content)
    # if not is_match:
    #     print('Error: Format incorrect!')
    #     sys.exit(-1)

    # select_categories = content.split(',')
    # select_categories = list(map(lambda y: int(y), filter(lambda x: re.match('\d+', x) and int(x) <= len(object_categories) and int(x) > 0, select_categories)))
    # if len(select_categories) == 0:
    #     print('Error: At least 1 items!')
    #     sys.exit(-1)

    category_items_list = []
    for category in object_categories:
        category_items_list.append(CategoryItems(category, list(filter(lambda x: x.endswith('png'), os.listdir('{0}/generated/extracted_object/{1}'.format(root_path, category))))))

    each_item_total_count = int(input('How many images for each item should be generated?\n'))
    if each_item_total_count < 2:
        print('Error: Generate count should not less than 2!')

    each_item_single_count = each_item_total_count // 2
    each_item_multi_count = each_item_total_count - each_item_single_count

    maximize_item_count = int(input('Please input the maximize item count in one image:\n'))
    if maximize_item_count < 1:
        print('Error: At least 1 item!')
        sys.exit(-1)

    for category_item in category_items_list:
        # generate single item image
        for _ in range(0, each_item_single_count):
            generate_one_image(root_path, backgrounds, [category_item], output_folder_prefix)
            pass

        # generate multi item image
        for _ in range(0, each_item_multi_count):
            src_list = category_items_list.copy()
            src_list.remove(category_item)
            items = random.sample(src_list, random.randint(1, maximize_item_count - 1))
            ls = [category_item]
            ls.extend(items)
            # print(','.join(list(map(lambda x: x.category, ls))))
            generate_one_image(root_path, backgrounds, ls, output_folder_prefix)

def cleanup(root_path: str):
    # clean up
    os.system('rm {0}/generated/training_image/*.jpg'.format(root_path))
    os.system('rm {0}/generated/training_image_with_item_border/*.jpg'.format(root_path))
    os.system('rm {0}/generated/training_image_info/*.xml'.format(root_path))

    os.system('rm {0}/generated/validation_image/*.jpg'.format(root_path))
    os.system('rm {0}/generated/validation_image_with_item_border/*.jpg'.format(root_path))
    os.system('rm {0}/generated/validation_image_info/*.xml'.format(root_path))

    os.system('rm {0}/generated/test_image/*.jpg'.format(root_path))
    os.system('rm {0}/generated/test_image_with_item_border/*.jpg'.format(root_path))
    os.system('rm {0}/generated/test_image_info/*.xml'.format(root_path))

