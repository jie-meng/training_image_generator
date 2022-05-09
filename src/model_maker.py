from cProfile import label
import sys
import tensorflow as tf
from tflite_model_maker import model_spec
from tflite_model_maker import object_detector
from src.utils import get_label_map

def make_model(root_path: str):
    assert tf.__version__.startswith('2')
    tf.get_logger().setLevel('ERROR')
    from absl import logging
    logging.set_verbosity(logging.ERROR)

    model_name = input('Please input name of to-be-generated model:\n').strip()
    if len(model_name) == 0:
        print('Error: invalid model name!')
        sys.exit(-1)

    print('Step 1. Choose an object detection model archiecture ...')
    # spec = model_spec.get('efficientdet_lite1')
    spec = object_detector.EfficientDetSpec(
        model_name='efficientdet-lite1',
        uri='https://tfhub.dev/tensorflow/efficientdet/lite1/feature-vector/1',
        hparams={'max_instances_per_image': 1000})

    print('Step 2. Load the dataset ...')
    label_map = get_label_map(root_path)
    # Load the dataset from pascal_voc
    train_data = object_detector.DataLoader.from_pascal_voc(images_dir = '{0}/generated/training_image'.format(root_path),
                                                            annotations_dir = '{0}/generated/training_image_info'.format(root_path),
                                                            label_map = label_map)

    validation_data = object_detector.DataLoader.from_pascal_voc(images_dir = '{0}/generated/validation_image'.format(root_path),
                                                                 annotations_dir = '{0}/generated/validation_image_info'.format(root_path),
                                                                 label_map=label_map)

    test_data = object_detector.DataLoader.from_pascal_voc(images_dir = '{0}/generated/test_image'.format(root_path),
                                                           annotations_dir = '{0}/generated/test_image_info'.format(root_path),
                                                           label_map = label_map)

    print('Step 3. Train the TensorFlow model with the training data ...')
    model = object_detector.create(train_data, model_spec = spec, batch_size = 10, train_whole_model = True, validation_data = validation_data)

    print('Step 4. Evaluate the model with the test data ...')
    model.evaluate(test_data)

    print('Step 5. Export as a TensorFlow Lite model ...')
    model.export(export_dir = '{0}/generated/model'.format(root_path), tflite_filename = '{0}.tflite'.format(model_name))

    print('Step 6. Evaluate the TensorFlow Lite model ...')
    model.evaluate_tflite('{0}/generated/model/{1}.tflite'.format(root_path, model_name), test_data)
