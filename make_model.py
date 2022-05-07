import os
from src.model_maker import make_model

if __name__ == "__main__":
    root_path = os.path.dirname(os.path.realpath(__file__))

    make_model(root_path)

