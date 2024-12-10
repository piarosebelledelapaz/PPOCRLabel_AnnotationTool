import argparse
import os
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def read_annotations(file_path):
    print(f"Reading annotations from {file_path}...")
    annotations = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) != 2:
                print(f"Skipping malformed line: {line}")
                continue
            image_name = parts[0].strip()
            annotation_str = parts[1].strip()
            if image_name not in annotations:
                annotations[image_name] = []

            try:
                image_annotations = json.loads(annotation_str)
                for annotation in image_annotations:
                    annotation['image_path'] = image_name
                    annotations[image_name].append(annotation)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError for {image_name}: {e}")
    # print(f"Loaded {len(annotations)} images with annotations.")
    return annotations


def calculate_center(points):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    center_x = np.mean(x_coords)
    center_y = np.mean(y_coords)
    return center_x, center_y


def link_annotations(annotations):
    # print("Linking annotations...")
    for image_name, image_annos in annotations.items():
        print(f"Processing image: {image_name}")
        id_counter = 1
        vaccine_names = [anno for anno in image_annos if anno['label'] == 'vaccine_name']
        vaccine_dates = [anno for anno in image_annos if anno['label'] == 'vaccine_date']

        for anno in image_annos:
            anno['id'] = id_counter
            anno['linking'] = []
            id_counter += 1

        for name_anno in vaccine_names:
            name_center = calculate_center(name_anno['points'])
            min_distance = float('inf')
            closest_date = None

            for date_anno in vaccine_dates:
                date_center = calculate_center(date_anno['points'])
                distance = np.abs(name_center[0] - date_center[0]) + np.abs(name_center[1] - date_center[1])
                if distance < min_distance:
                    closest_date = date_anno
                    min_distance = distance

            if closest_date:
                name_anno['linking'].append([name_anno['id'], closest_date['id']])
                closest_date['linking'].append([name_anno['id'], closest_date['id']])
        print(f"Linked {len(vaccine_names)} vaccine names to dates for image {image_name}.\n")
    return annotations


def save_annotations(annotations, file_path):
    print(f"\nSaving annotations to {file_path}...")
    grouped_annotations = {}
    for image_path, annos in annotations.items():
        for anno in annos:
            anno.pop('image_path', None)
            if 'difficult' in anno:
                del anno['difficult']
        grouped_annotations[image_path] = annos

    with open(file_path, 'w', encoding='utf-8') as f:
        for image_path, annos in grouped_annotations.items():
            annotations_json = json.dumps(annos, ensure_ascii=False)
            f.write(f"{image_path}\t{annotations_json}\n")
    print("Annotations saved. \n")
    return file_path



def visualize_annotations(image_path, annotations, save_path=None):
    # print(f"Visualizing annotations for {image_path}...")
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", size=20)
    except IOError:
        font = ImageFont.load_default()

    for anno in annotations:
        points = anno['points']
        xmin, ymin = np.min(points, axis=0)
        xmax, ymax = np.max(points, axis=0)

        draw.rectangle([xmin, ymin, xmax, ymax], outline='red', width=6)

        draw.text((xmin, ymin - 20), str(anno['id']), font=font, fill='red')

        if 'linking' in anno and anno['linking']:
            for link in anno['linking']:
                name_id, date_id = link
                name_anno = next(filter(lambda x: x['id'] == name_id, annotations), None)
                date_anno = next(filter(lambda x: x['id'] == date_id, annotations), None)

                if name_anno and date_anno:
                    name_center = calculate_center(name_anno['points'])
                    date_center = calculate_center(date_anno['points'])

                    draw.line([name_center, date_center], fill='#39FF14', width=10)

                    mid_x = (name_center[0] + date_center[0]) / 2
                    mid_y = (name_center[1] + date_center[1]) / 2

                    draw.text((mid_x, mid_y), f"{name_id}-{date_id}", font=font, fill='#39FF14')

    if save_path:
        image.save(save_path)
        print(f"Saved visualization to {save_path}")


def visualize_and_save_all_images(annotations_file, output_folder):
    # print(f"Reading annotations for visualization from {annotations_file}...")
    annotations = read_annotations(annotations_file)
    # print(f"Creating output folder: {output_folder}...")
    os.makedirs(output_folder, exist_ok=True)
    for image_name, image_annos in annotations.items():
        # print(f"Processing visualization for {image_name}...")
        save_path = os.path.join(output_folder, f"{os.path.basename(image_name).split('.')[0]}_annotations.jpeg")
        visualize_annotations(image_name, image_annos, save_path)


def main():
    parser = argparse.ArgumentParser(description="Annotation linking and visualization tool.")
    parser.add_argument("--label-txt", required=True, help="Path to the annotation file.")
    parser.add_argument("--output-folder", required=True, help="Path to save visualized images.")
    args = parser.parse_args()

    # print("Starting annotation linking and visualization process...")
    annotations = read_annotations(args.label_txt)
    annotations = link_annotations(annotations)
    processed_file_path = save_annotations(annotations, args.label_txt.replace('.txt', '_linked.txt'))
    visualize_and_save_all_images(processed_file_path, args.output_folder)
    # print("Process completed.")


if __name__ == "__main__":
    main()
