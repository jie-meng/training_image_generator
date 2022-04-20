import os
import sys
import shutil

def extract_objects(root_path: str):
    object_categories = list(filter(lambda x: os.path.isdir(root_path + '/generated/object/' + x), os.listdir(root_path + '/generated/object')))

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
                os.system('convert {0} -trim +repage {0}'.format(target_image))
