import os
import sys
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
from src.utils import get_extracted_object_categories, load_classes


def preprocess_image(image_path, input_size):
  """Preprocess the input image to feed to the TFLite model"""
  img = tf.io.read_file(image_path)
  img = tf.io.decode_image(img, channels=3)
  img = tf.image.convert_image_dtype(img, tf.uint8)
  original_image = img
  resized_img = tf.image.resize(img, input_size)
  resized_img = resized_img[tf.newaxis, :]
  resized_img = tf.cast(resized_img, dtype=tf.uint8)
  return resized_img, original_image


def detect_objects(interpreter, image, threshold, classes):
  """Returns a list of detection results, each a dictionary of object info."""
  signature_fn = interpreter.get_signature_runner()

  # Feed the input image to the model
  output = signature_fn(images=image)

  # Get all outputs from the model
  count = int(np.squeeze(output['output_0']))
  scores = np.squeeze(output['output_1'])
  classes = np.squeeze(output['output_2'])
  boxes = np.squeeze(output['output_3'])

  results = []
  for i in range(count):
    if scores[i] >= threshold:
      result = {
        'bounding_box': boxes[i],
        'class_id': classes[i],
        'score': scores[i]
      }
      results.append(result)
  return results


def run_odt_and_draw_results(image_path, interpreter, threshold, classes):
  """Run object detection on the input image and draw the detection results"""
  # Load the input shape required by the model
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

  # Load the input image and preprocess it
  preprocessed_image, original_image = preprocess_image(
      image_path,
      (input_height, input_width)
    )

  # Run object detection on the input image
  results = detect_objects(interpreter, preprocessed_image, threshold, classes)

  # Plot the detection results on the input image
  original_image_np = original_image.numpy().astype(np.uint8)
  for obj in results:
    # Convert the object bounding box from relative coordinates to absolute
    # coordinates based on the original image resolution
    ymin, xmin, ymax, xmax = obj['bounding_box']
    xmin = int(xmin * original_image_np.shape[1])
    xmax = int(xmax * original_image_np.shape[1])
    ymin = int(ymin * original_image_np.shape[0])
    ymax = int(ymax * original_image_np.shape[0])

    # Find the class index of the current object
    class_id = int(obj['class_id'])

    # Draw the bounding box and label on the image
    COLORS = np.random.randint(0, 255, size=(len(classes), 3), dtype=np.uint8)
    color = [int(c) for c in COLORS[class_id]]
    cv2.rectangle(original_image_np, (xmin, ymin), (xmax, ymax), color, 2)
    # Make adjustments to make the label visible for all objects
    y = ymin - 15 if ymin - 15 > 15 else ymin + 15
    label = "{}: {:.0f}%".format(classes[class_id], obj['score'] * 100)
    cv2.putText(original_image_np, label, (xmin, y),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

  # Return the final image
  original_uint8 = original_image_np.astype(np.uint8)
  return original_uint8


def test(root_path: str):
  #@title Run object detection and show the detection results
  DETECTION_THRESHOLD = 0.3

  models = list(filter(lambda x: x.endswith('.tflite'), os.listdir(root_path + '/generated/model')))
  models.sort()
  print('Please select a model:')
  for index, model in enumerate(models):
    print('{0}. {1}'.format(index + 1, model))

  selection = int(input())
  if selection > len(models) or selection < 1:
      print('Error: selection out of range!')
      sys.exit(-1)

  model = models[selection - 1]

  # Load the TFLite model
  interpreter = tf.lite.Interpreter(model_path = '{0}/generated/model/{1}'.format(root_path, model))
  interpreter.allocate_tensors()

  model_base_name = os.path.splitext(model)[0]
  classes = load_classes(root_path, model_base_name)
  if len(classes) == 0:
    print('Error: load_classes failed')
    sys.exit(-1)

  check_images = list(filter(lambda x: x.endswith('.jpg'), os.listdir('{0}/generated/check_image'.format(root_path))))
  for image in check_images:
    check_result_file = '{0}/generated/check_result/{1}_{2}'.format(root_path, model_base_name, image)
    if not os.path.isfile(check_result_file):
      # Run inference and draw detection result on the local copy of the original file
      detection_result_image = run_odt_and_draw_results(
        '{0}/generated/check_image/{1}'.format(root_path, image),
        interpreter,
        DETECTION_THRESHOLD,
        classes
      )

      # Show the detection result
      output_im = Image.fromarray(detection_result_image)
      output_im.save(check_result_file)
      output_im.close()
