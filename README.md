# training_image_generator

## Prepare

OS: MacOS

python3.9+

```
brew install ffmpeg imagemagick

pip3 install --upgrade pip
pip3 install --use-deprecated=legacy-resolver

pip3 install backgroundremover
pip3 install tflite-model-maker
pip3 install pycocotools

```

## make image

```
python3 make_image.py

```

Then follow the tips:

### 1. Retrieve images from android mobile phone

If you want to prepare the images of object __bottle__, take pictures of bottles with your android device (You should always take photo with landscape mode, do not use potrait mode, otherwise the extracting object work will not work as you expected). When you captured enough bottle images, connect the android device to your computer, make sure adb works.

Make a sub dir __bottle__ under the path _generated/object_ before you run `python3 make_image.py`. Then type __1__ to select 'Retrieve images from android mobile phone'.

Then select the number before __bottle__.

When you see 'How many images to retrieve (lates)?', input the numbers of pictures you took for the bottles. Type enter then the pictures would be downloaded to the _generated/object/bottle_ directory.

### 2. Retrieve videos from android mobile phone

If you want to prepare the background images, you can capture some mp4 videos with your android device. Then connect the android device to your computer, make sure adb works.

Select __2__ 'Retrieve videos from android mobile phone' after you run `python3 make_image.py`. Then type the video numbers you captured. Type enter then the videos would be downloaded to the _generated/background/video_ directory.

### 3. Convert video to images

After you got background videos under the _generated/background/video_ directory, you need to convert them to images.

Select the source background (video). Then input the crop size of the mp4. (e.g. The video might be 4000*3000, you many want the image with width 1000 and height 1000, from the position x = 0, y = 1000.)

Every 0.5 seconds of the video make an image, which means a 30-seconds-long mp4 would generate 60 background images. The output background image would generated under the directory _generated/background/image_.

### 4. Resize background image

If you already have the background image with a big size, you want to resize it with an appropriate ratio. You can use this command to change the resolution of background images batch.

### 5. Extract objects

The object images are captured with background, you should always extract object out of the background.

Input the resize ratio to fit the background size and do extracting. The output images would generated under the directory _generated/extracted_object_. Sub folders would generate automatically.

If some of the extract images does not fit the size you want, you can delete them and do extract again. Extract objects would only deal with the non-existed object.

### 6. Generate training image

First select the objects you want to put into the training images. You can select either single or multiple object.

Then input how many images you want to generated.

Training image would be generated under the directory _generated/training_image_.

Training image info (xml) would be generated under the directory _generated/training_image_info_.

Training image with item border would be generated under the directory _generated/training_image_with_item_border_.

### 7. Generate validation image

First select the objects you want to put into the validation images. You can select either single or multiple object.

Then input how many images you want to generated.

Validation image would be generated under the directory _generated/validation_image_.

Validation image info (xml) would be generated under the directory _generated/validation_image_info_.

Validation image with item border would be generated under the directory _generated/validation_image_with_item_border_.

### 8. Generate test image

First select the objects you want to put into the test images. You can select either single or multiple object.

Then input how many images you want to generated.

Test image would be generated under the directory _generated/test_image_.

Test image info (xml) would be generated under the directory _generated/test_image_info_.

Test image with item border would be generated under the directory _generated/test_image_with_item_border_.

### 9. Clean up training images

Clean up training, validation and test images and related files.


## make model 

```
python3 make_model.py

```

You can have many models, so input the model name.

Then the script will create model based on current training, validation and test images.

## check model

```
python3 check_model.py

```

### 1. Retrieve check images from android mobile phone

Prepare the images for checking the model generated.

When you see 'How many images to retrieve (lates)?', input the numbers of pictures you took for checking.


### 2. Check model

First you should select model for checking.

Then the script will apply model checking with the images under folder _generated/check_image_, result images would under folder _generated/check_result_.

