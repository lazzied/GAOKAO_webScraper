import os
import requests
from PIL import Image

def download_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Image saved to {save_path}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading image: {e}")

def resize_image(image_path, folder_name):
    try:
        a4_width = 2480
        a4_height = 3508

        img = Image.open(image_path)
        original_width, original_height = img.size
        aspect_ratio = original_width / float(original_height)

        if aspect_ratio > 1:
            new_width = a4_width
            new_height = int(a4_width / aspect_ratio)
        else:
            new_height = a4_height
            new_width = int(a4_height * aspect_ratio)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        left = (new_width - a4_width) / 2
        top = (new_height - a4_height) / 2
        right = (new_width + a4_width) / 2
        bottom = (new_height + a4_height) / 2

        img = img.crop((left, top, right, bottom))

        output_path = os.path.join(folder_name, "resized_a4_" + os.path.basename(image_path).replace(".jpg", ".png"))
        img.save(output_path)
        print(f"Resized image saved to {output_path}")

    except Exception as e:
        print(f"Error resizing image: {e}")

def images_to_pdf(image_paths, pdf_path):
    try:
        images = [Image.open(image_path).convert("RGB") for image_path in image_paths]
        images[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )
        print(f"PDF created at {pdf_path}")

        for image_path in image_paths:
            try:
                os.remove(image_path)
                print(f"Deleted {image_path}")
            except Exception as e:
                print(f"Failed to delete {image_path}: {e}")
    except Exception as e:
        print(f"Error creating PDF: {e}")
