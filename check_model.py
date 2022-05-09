import os
from src.adb import retrieve_check_images_from_phone
from src.model_tester import test
from src.utils import Proc


if __name__ == "__main__":
    root_path = os.path.dirname(os.path.realpath(__file__))

    procs = []
    procs.append(Proc('Retrieve check images from android mobile phone', retrieve_check_images_from_phone))
    procs.append(Proc('Check model', test))

    print('Select:')
    for index, proc in enumerate(procs):
        print('{0}. {1}'.format(index + 1, proc.name))

    selection = int(input())
    if selection > len(procs) or selection < 1:
        print('Error: selection out of range!')
        sys.exit(-1)

    procs[selection - 1].func(root_path)

