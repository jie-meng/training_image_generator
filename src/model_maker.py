import numpy as np
import os
import tensorflow as tf
from tflite_model_maker.config import QuantizationConfig
from tflite_model_maker.config import ExportFormat
from tflite_model_maker import model_spec
from tflite_model_maker import object_detector

def make_model(root_path: str):
    assert tf.__version__.startswith('2')
    tf.get_logger().setLevel('ERROR')
    from absl import logging
    logging.set_verbosity(logging.ERROR)

    print('Step 1. Choose an object detection model archiecture ...')
    # spec = model_spec.get('efficientdet_lite1')
    spec = object_detector.EfficientDetSpec(
        model_name='efficientdet-lite2',
        uri='https://tfhub.dev/tensorflow/efficientdet/lite1/feature-vector/1',
        hparams={'max_instances_per_image': 1000})

    print('Step 2. Load the dataset ...')
    # Load the dataset from pascal_voc
    train_data = object_detector.DataLoader.from_pascal_voc(images_dir = '{0}/generated/training_image'.format(root_path),
                                                            annotations_dir = '{0}/generated/training_image_info'.format(root_path),
                                                            label_map={ 1: 'chair', 2: 'bottle' })

    validation_data = object_detector.DataLoader.from_pascal_voc(images_dir = '{0}/generated/validation_image'.format(root_path),
                                                                 annotations_dir = '{0}/generated/validation_image_info'.format(root_path),
                                                                 label_map={ 1: 'chair', 2: 'bottle' })

    test_data = object_detector.DataLoader.from_pascal_voc(images_dir = '{0}/generated/test_image'.format(root_path),
                                                           annotations_dir = '{0}/generated/test_image_info'.format(root_path),
                                                           label_map={ 1: 'chair', 2: 'bottle' })

    print('Step 3. Train the TensorFlow model with the training data ...')
    model = object_detector.create(train_data, model_spec = spec, batch_size = 80, train_whole_model = True, validation_data = validation_data)

    print('Step 4. Evaluate the model with the test data ...')
    model.evaluate(test_data)

    print('Step 5. Export as a TensorFlow Lite model ...')
    model.export(export_dir = '.', tflite_filename = 'furniture.tflite')

    print('Step 6. Evaluate the TensorFlow Lite model ...')
    model.evaluate_tflite('furniture.tflite', test_data)

