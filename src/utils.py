import os
import json
from typing import List, Dict, Tuple, Callable

class CategoryItems(object):
    def __init__(self, category: str, items: List[str]):
        self.__category = category
        self.__items = items

    @property
    def category(self) -> str:
        return self.__category

    @property
    def items(self) -> List[str]:
        return self.__items


class TrainingItemInfo(object):
    def __init__(self, category: str, name: str):
        self.__category = category
        self.__name = name
        self.__position = (0, 0)
        self.__width = 0
        self.__height = 0
        self.__is_covered = False

    @property
    def category(self) -> str:
        return self.__category

    @property
    def name(self) -> str:
        return self.__name

    @property
    def position(self) -> Tuple[int]:
        return self.__position

    @position.setter
    def position(self, value: Tuple[int]):
        self.__position = value

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, value: int):
        self.__width = value

    @property
    def height(self) -> int:
        return self.__height

    @height.setter
    def height(self, value: int) -> int:
        self.__height = value

    @property
    def is_covered(self) -> bool:
        return self.__is_covered

    @is_covered.setter
    def is_covered(self, value: bool):
        self.__is_covered = value


class CompositeImageInfo(object):
    def __init__(self, filename: str, width: int, height: int, training_items: List[TrainingItemInfo]):
        self.__filename = filename
        self.__width = width
        self.__height = height
        self.__training_items = training_items

    @property
    def filename(self) -> str:
        return self.__filename

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def training_items(self) -> List[TrainingItemInfo]:
        return self.__training_items


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

def is_intersection(xmin_a: int, xmax_a: int, ymin_a: int, ymax_a: int, xmin_b: int, xmax_b: int, ymin_b: int, ymax_b: int) -> bool:
    intersection_flag = True

    minx = max(xmin_a, xmin_b)
    miny = max(ymin_a, ymin_b)

    maxx = min(xmax_a, xmax_b)
    maxy = min(ymax_a, ymax_b)

    if minx > maxx or miny > maxy:
        intersection_flag = False

    return intersection_flag

def get_object_categories(root_path: str) -> List[str]:
    object_categories = list(filter(lambda x: os.path.isdir(root_path + '/generated/object/' + x), os.listdir(root_path + '/generated/object')))
    object_categories.sort()
    return object_categories

def get_extracted_object_categories(root_path: str) -> List[str]:
    object_categories = list(filter(lambda x: os.path.isdir(root_path + '/generated/extracted_object/' + x), os.listdir(root_path + '/generated/extracted_object')))
    object_categories.sort()
    return object_categories

def get_label_map(root_path: str) -> Dict[int, str]:
    object_categories = get_extracted_object_categories(root_path)
    label_map = {}
    for index, object in enumerate(object_categories):
        label_map[index + 1] = object

    return label_map

def save_label_map(root_path: str, model_name: str, label_map: Dict[int, str]):
    with open('{0}/generated/model/{1}_label_map.json'.format(root_path, model_name), 'w') as label_name_file:
        json.dump(label_map, label_name_file, indent = 4)

def load_label_map(root_path: str, model_name: str) -> Dict[int, str]:
    with open('{0}/generated/model/{1}_label_map.json'.format(root_path, model_name)) as label_name_file:
        return json.load(label_name_file)

def load_classes(root_path: str, model_name: str) -> List[str]:
    label_map = load_label_map(root_path, model_name)

    classes = ['???'] * len(label_map)
    for label_id, label_name in label_map.items():
        classes[int(label_id)-1] = label_name

    return classes
