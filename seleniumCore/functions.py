import os
import requests
from PIL import Image

import requests
import time

import requests
import time
import os

def download_image(image_url, save_path, max_retries=3, timeout=15):

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[Attempt {attempt}] Downloading image: {image_url}")
            response = requests.get(image_url, timeout=timeout)
            response.raise_for_status()

            # Create folder if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save the image
            with open(save_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ Downloaded successfully: {save_path}")
            return True

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout on attempt {attempt} for image: {image_url}")
        except requests.exceptions.ConnectionError:
            print(f"🚫 Connection error on attempt {attempt} for image: {image_url}")
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error ({e.response.status_code}) for image: {image_url}")
            # If it's a 404 or 403, don't bother retrying
            if e.response.status_code in [403, 404]:
                break
        except Exception as e:
            print(f"⚠️ Unexpected error on attempt {attempt}: {e}")

        # Exponential backoff before retrying
        time.sleep(2 ** attempt)

    print(f"❌ Failed to download after {max_retries} attempts: {image_url}")
    return False


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
