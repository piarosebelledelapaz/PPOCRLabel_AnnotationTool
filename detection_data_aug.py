import os
import json
import argparse
from PIL import Image

# Flip annotation points horizontally
def flip_points(points, image_width):
    return [[image_width - point[0], point[1]] for point in points]

def main(annotation_file_path, image_folder, output_image_folder, output_annotation_file_path):
    # Ensure the output folder exists
    os.makedirs(output_image_folder, exist_ok=True)

    # Read annotations
    with open(annotation_file_path, 'r', encoding='utf-8') as file:
        annotations = file.readlines()

    flipped_annotations = []

    for annotation in annotations:
        parts = annotation.strip().split('\t')

        if len(parts) != 2:
            print(f"Unexpected format: {annotation}")
            continue

        image_name = parts[0]

        try:
            annotation_data = json.loads(parts[1])
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e} in annotation {annotation}")
            continue

        image_path = os.path.join(image_folder, image_name).replace('\\', '/')

        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            continue

        try:
            image = Image.open(image_path)
        except Exception as e:
            print(f"Error opening image file {image_path}: {e}")
            continue

        image_width = image.width

        # Flip the image horizontally
        flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)

        # Convert RGBA to RGB if necessary
        if flipped_image.mode == 'RGBA':
            flipped_image = flipped_image.convert('RGB')

        # Rename and save the flipped image
        flipped_image_name = os.path.splitext(image_name)[0] + "_flipped.jpeg"
        flipped_image_path = os.path.join(output_image_folder, flipped_image_name)
        flipped_image.save(flipped_image_path)

        # Flip annotation points and update annotation data
        for annot in annotation_data:
            annot['points'] = flip_points(annot['points'], image_width)

        flipped_annotations.append((flipped_image_name, annotation_data))

    # Save updated annotations
    with open(output_annotation_file_path, 'w', encoding='utf-8') as output_file:
        for image_name, annotation_data in flipped_annotations:
            output_file.write(image_name + '\t' + json.dumps(annotation_data, ensure_ascii=False) + '\n')

    print("Flipped images saved to", output_image_folder)
    print("Annotations updated and saved to", output_annotation_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flip images and update annotations.")
    parser.add_argument("annotation_file", help="Path to the annotation file (txt format).")
    parser.add_argument("image_folder", help="Path to the folder containing the images.")
    parser.add_argument("output_image_folder", help="Path to the folder to save flipped images.")
    parser.add_argument("output_annotation_file", help="Path to save the updated annotation file.")

    args = parser.parse_args()

    main(args.annotation_file, args.image_folder, args.output_image_folder, args.output_annotation_file)
