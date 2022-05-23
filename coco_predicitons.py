import tensorflow as tf
import numpy as np
import json
import os
import sys
from src.utils import load_classes
from PIL import Image

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


def detect_objects(interpreter, image_path, threshold):
  """Returns a list of detection results, each a dictionary of object info."""

  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

  image_content = Image.open(os.path.join(image_path))

  w, h = image_content.size

   # Load the input image and preprocess it
  preprocessed_image, original_image = preprocess_image(
      image_path,
    (input_height, input_width)
       )
  signature_fn = interpreter.get_signature_runner()

  # Feed the input image to the model
  output = signature_fn(images=preprocessed_image)

  # Get all outputs from the model
  count = int(np.squeeze(output['output_0']))
  scores = np.squeeze(output['output_1'])
  classes = np.squeeze(output['output_2'])
  boxes = np.squeeze(output['output_3'])
  #print(classes)

  # Plot the detection results on the input image
  original_image_np = original_image.numpy().astype(np.uint8)

  results = []
  for i in range(count):
    if scores[i] >= threshold:
      ymin, xmin, ymax, xmax = boxes[i]
      xmin = int(xmin * original_image_np.shape[1])
      xmax = int(xmax * original_image_np.shape[1])
      ymin = int(ymin * original_image_np.shape[0])
      ymax = int(ymax * original_image_np.shape[0])
      image = image_path.split('/')[-1]
      print(image)
      result = {
        'image_id': int(image.split('.')[0][5:]),
        'bbox': [xmin,ymin,xmax-xmin,ymax-ymin],
        'category_id': int(classes[i]),
        'score': float(scores[i])
      }
      results.append(result)
      
  image_results = {'id':int(image_path.split('/')[-1].split('.')[0][5:]),'file_name':image_path.split('/')[-1], 'width': float(w), 'height': float(h)}
  return results, image_results


def create_coco_predicitons(root_path, threshold):

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
      #output = []

      json_context = {'annotations':[], 'images':[], 'categories':[]}
      for i, category in enumerate(classes):
          json_context['categories'].append({'id':int(i), 'name':category})

      for image in check_images:
          # Run inference and draw detection result on the local copy of the original file
          results, image_results = detect_objects(interpreter, '{0}/generated/check_image/{1}'.format(root_path, image), threshold)
          json_context['annotations'].extend(results)
          json_context['images'].append(image_results)

      
      if not os.path.exists('{0}/generated/check_predictions'.format(root_path)):
            os.mkdir('{0}/generated/check_predictions'.format(root_path))
      
      pred_file = '{0}/generated/check_predictions/{1}_{2}'.format(root_path, model_base_name, 'coco_predictions.json')
      with open(pred_file, "w") as f:
            json.dump(json_context, f, indent=4)
            print('COCO predictions are generated')

      return 

if __name__ == "__main__":
    DETECTION_THRESHOLD = float(sys.argv[1])
    root_path = os.path.dirname(os.path.realpath(__file__))
    create_coco_predicitons(root_path, DETECTION_THRESHOLD)

