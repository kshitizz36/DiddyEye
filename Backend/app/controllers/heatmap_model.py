import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt


# Define image size based on model input shape
IMAGE_SIZE = (224, 224)


def preprocess_image(image):
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    image = image.resize(IMAGE_SIZE)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = image / 255.0
    return image

def generate_gradcam_heatmap(model, img_array, last_conv_layer_name="out_relu", pred_index=None):
    grad_model = tf.keras.models.Model([model.inputs], [model.get_layer(last_conv_layer_name).output, model.output])
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = np.maximum(heatmap, 0) / np.max(heatmap)
    return heatmap

def overlay_heatmap_on_image(img, heatmap, alpha=0.4):
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap = np.uint8(255 * heatmap)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    superimposed_img = cv2.addWeighted(img, 1 - alpha, heatmap, alpha, 0)
    superimposed_img = cv2.cvtColor(superimposed_img, cv2.COLOR_BGR2RGB)
    return superimposed_img

def classify_image_with_gradcam(image_data,model):
    processed_image = preprocess_image(image_data)
    prediction = model.predict(processed_image)
    class_label = int(np.round(prediction[0][0]))
    confidence = prediction[0][0]

    heatmap = generate_gradcam_heatmap(model, processed_image)
    overlay_img = overlay_heatmap_on_image(image_data, heatmap)
    return class_label, confidence, overlay_img




def heatmap_creator(file_path,model):
    # Open your image (or do your Grad-CAM logic)

    image = Image.open(file_path)
    class_label, confidence, overlay_img = classify_image_with_gradcam(image,model)

    print(f"{class_label} {confidence}")

    # 1) Extract the file name and extension from file_path
    base_name, ext = os.path.splitext(file_path)  # e.g., "image", ".jpg"

    # 2) Construct the output file path by appending "_heatmap" before the extension
    output_filename = f"{base_name}_heatmap{ext}"  # e.g., "image_heatmap.jpg"

    # 3) Save the heatmap
    plt.imshow(overlay_img)
    plt.axis('off')
    plt.savefig(output_filename, bbox_inches='tight', pad_inches=0)
    plt.close()  # free memory

    # 4) Return or print the new file path
    return output_filename
