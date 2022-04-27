import os
import xml.etree.ElementTree as ET
from typing import List
from src.model import CompositeImageInfo

def generate_xml(root_path: str, composite_image_info: CompositeImageInfo):
    file_basename = os.path.basename(composite_image_info.filename)

    root_ele = ET.Element('annotation')

    folder_ele = ET.SubElement(root_ele, 'folder')
    folder_ele.text = 'Unknown'

    filename_ele = ET.SubElement(root_ele, 'filename')
    filename_ele.text = file_basename

    path_ele = ET.SubElement(root_ele, 'path')
    path_ele.text = composite_image_info.filename

    source_ele = ET.SubElement(root_ele, 'source')
    database_ele = ET.SubElement(source_ele, 'database')
    database_ele.text = 'Unknown'

    size_ele = ET.SubElement(root_ele, 'size')
    width_ele = ET.SubElement(size_ele, 'width')
    width_ele.text= str(composite_image_info.width)
    height_ele = ET.SubElement(size_ele, 'height')
    height_ele.text = str(composite_image_info.height)
    depth_ele = ET.SubElement(size_ele, 'depth')
    depth_ele.text = '3'

    segmented_ele = ET.SubElement(root_ele, 'segmented')
    segmented_ele.text = '0'

    for item in composite_image_info.training_items:
        object_ele = ET.SubElement(root_ele, 'object')

        object_name_ele = ET.SubElement(object_ele, 'name')
        object_name_ele.text = item.category

        pose_ele = ET.SubElement(object_ele, 'pose')
        pose_ele.text = 'Unspecified'

        truncated_ele = ET.SubElement(object_ele, 'truncated')
        truncated_ele.text = '1' if item.is_truncated else '0'

        difficult_ele = ET.SubElement(object_ele, 'difficult')
        difficult_ele.text = '0'

        bndbox_ele = ET.SubElement(object_ele, 'bndbox')

        bndbox_xmin_ele = ET.SubElement(bndbox_ele, 'xmin')
        bndbox_xmin_ele.text = str(item.position[0])

        bndbox_ymin_ele = ET.SubElement(bndbox_ele, 'ymin')
        bndbox_ymin_ele.text = str(item.position[1])

        bndbox_xmax_ele = ET.SubElement(bndbox_ele, 'xmax')
        bndbox_xmax_ele.text = str(item.position[0] + item.width)

        bndbox_ymax_ele = ET.SubElement(bndbox_ele, 'ymax')
        bndbox_ymax_ele.text = str(item.position[1] + item.height)

    tree = ET.ElementTree(root_ele)
    ET.indent(tree, space='\t', level = 0)

    tree.write('{0}/generated/training_image_info/{1}.xml'.format(root_path, file_basename.replace('.png', '')))

