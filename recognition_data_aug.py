import os
from PIL import Image
import argparse


class ImageAnnotationProcessor:
    def __init__(self, annotation_file, image_dir, output_annotation_file, output_image_dir):
        self.annotation_file = annotation_file
        self.image_dir = image_dir
        self.output_annotation_file = output_annotation_file
        self.output_image_dir = output_image_dir

    # Get the word in reverse order
    @staticmethod
    def reverse_string(s):
        return s[::-1]

    # Flip image horizontally and save it with a new name
    @staticmethod
    def flip_image(image_path, new_image_path):
        try:
            image = Image.open(image_path)
            flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
            flipped_image.save(new_image_path)
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")

    # Update annotation file with reversed strings and flipped image names
    def update_annotations(self):
        flipped_annotations = []
        with open(self.annotation_file, 'r', encoding='utf-8') as f_in:
            for line in f_in:
                parts = line.strip().split('\t')
                if len(parts) != 2:
                    print(f"Invalid line format: {line.strip()}")
                    continue

                image_name, annotation = parts
                flipped_image_name = image_name.replace('.jpg', '_flipped.jpeg')
                flipped_annotation = self.reverse_string(annotation)
                flipped_annotations.append((flipped_image_name, flipped_annotation))

        # Write updated annotations to the output file
        with open(self.output_annotation_file, 'w', encoding='utf-8') as f_out:
            for flipped_image_name, flipped_annotation in flipped_annotations:
                f_out.write(f"{flipped_image_name}\t{flipped_annotation}\n")

    # Process all images and annotations
    def process(self):
        os.makedirs(self.output_image_dir, exist_ok=True)
        self.update_annotations()

        with open(self.annotation_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) != 2:
                    continue

                image_name = parts[0]
                input_image_path = os.path.join(self.image_dir, image_name)
                output_image_name = image_name.replace('.jpg', '_flipped.jpeg')
                output_image_path = os.path.join(self.output_image_dir, output_image_name)

                if os.path.exists(input_image_path):
                    self.flip_image(input_image_path, output_image_path)
                else:
                    print(f"Image not found: {input_image_path}")

        print("Flipped images saved to", self.output_image_dir)
        print("Annotations updated and saved to", self.output_annotation_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flip images and update annotations.")
    parser.add_argument("annotation_file", help="Path to the annotation file (txt format).")
    parser.add_argument("image_dir", help="Path to the folder containing the images.")
    parser.add_argument("output_annotation_file", help="Path to save the updated annotation file.")
    parser.add_argument("output_image_dir", help="Path to the folder to save flipped images.")

    args = parser.parse_args()

    processor = ImageAnnotationProcessor(
        annotation_file=args.annotation_file,
        image_dir=args.image_dir,
        output_annotation_file=args.output_annotation_file,
        output_image_dir=args.output_image_dir
    )
    processor.process()
