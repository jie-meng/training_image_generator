from typing import List, Tuple

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
        self.__is_truncated = False

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
    def is_truncated(self) -> bool:
        return self.__is_truncated

    @is_truncated.setter
    def is_truncated(self, value: bool):
        self.__is_truncated = value


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

