import requests
from PIL import Image, ImageDraw, ImageFont
import io
from typing import List, Tuple


class ImageGridCreator:
    def __init__(self, grid_size: Tuple[int, int] = (800, 800)):
        """
        Initialize the ImageGridCreator

        Args:
            grid_size: Tuple of (width, height) for the final grid image
        """
        self.grid_size = grid_size
        self.medal_colors = {
            1: '#FFD700',  # Gold
            2: '#C0C0C0',  # Silver
            3: '#CD7F32',  # Bronze
            4: '#4A4A4A'  # Gray for 4th place
        }

    def download_image(self, url: str) -> Image.Image:
        """
        Download an image from URL and return PIL Image object

        Args:
            url: Image URL to download

        Returns:
            PIL Image object
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            return image.convert('RGB')
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")
            # Create a placeholder image if download fails
            placeholder = Image.new('RGB', (400, 300), color='lightgray')
            draw = ImageDraw.Draw(placeholder)
            draw.text((200, 150), "Image Not Found", fill='black', anchor='mm')
            return placeholder

    def create_medal(self, place: int, size: int = 60) -> Image.Image:
        """
        Create a medal image for the given place

        Args:
            place: Place number (1-4)
            size: Size of the medal in pixels

        Returns:
            PIL Image object of the medal
        """
        medal = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(medal)

        # Draw medal circle
        color = self.medal_colors.get(place, '#4A4A4A')
        draw.ellipse([5, 5, size - 5, size - 5], fill=color, outline='black', width=2)

        # Add place number
        try:
            # Try to use default font, fall back to basic if not available
            font = ImageFont.truetype("arial.ttf", size // 3)
        except:
            font = ImageFont.load_default()

        # Draw the place number
        text = str(place)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        draw.text((x, y), text, fill='white', font=font, stroke_width=1, stroke_fill='black')

        return medal

    def resize_image_to_fit(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        Resize image to fit within target size while maintaining aspect ratio

        Args:
            image: PIL Image to resize
            target_size: Target (width, height)

        Returns:
            Resized PIL Image
        """
        image.thumbnail(target_size, Image.Resampling.LANCZOS)

        # Create new image with target size and paste resized image in center
        new_image = Image.new('RGB', target_size, 'white')
        x = (target_size[0] - image.width) // 2
        y = (target_size[1] - image.height) // 2
        new_image.paste(image, (x, y))

        return new_image

    def create_grid(self, image_urls: List[str]) -> Image.Image:
        """
        Create a 2x2 grid from 4 image URLs with medals

        Args:
            image_urls: List of 4 image URLs

        Returns:
            PIL Image object of the final grid
        """
        if len(image_urls) != 4:
            raise ValueError("Exactly 4 image URLs are required")

        # Calculate individual image size (half of grid size)
        individual_width = self.grid_size[0] // 2
        individual_height = self.grid_size[1] // 2
        individual_size = (individual_width, individual_height)

        # Download and resize images
        images = []
        for url in image_urls:
            img = self.download_image(url)
            img = self.resize_image_to_fit(img, individual_size)
            images.append(img)

        # Create the final grid image
        grid_image = Image.new('RGB', self.grid_size, 'white')

        # Position images in grid
        positions = [
            (individual_width, 0),  # Top right (1st place)
            (0, 0),  # Top left (2nd place)
            (individual_width, individual_height),  # Bottom right (3rd place)
            (0, individual_height)  # Bottom left (4th place)
        ]

        # Paste images and add medals
        for i, (img, pos) in enumerate(zip(images, positions)):
            # Paste the image
            grid_image.paste(img, pos)

            # Create and paste medal
            medal = self.create_medal(i + 1)
            medal_x = pos[0] + individual_width - medal.width - 10
            medal_y = pos[1] + 10

            # Paste medal with transparency
            if medal.mode == 'RGBA':
                grid_image.paste(medal, (medal_x, medal_y), medal)
            else:
                grid_image.paste(medal, (medal_x, medal_y))

        return grid_image

    def save_grid(self, image_urls: List[str], output_path: str = "image_grid.jpg"):
        """
        Create and save the image grid

        Args:
            image_urls: List of 4 image URLs
            output_path: Path to save the final image
        """
        grid_image = self.create_grid(image_urls)
        grid_image.save(output_path, quality=95)
        print(f"Grid image saved as {output_path}")

        return grid_image

# Example usage
if __name__ == "__main__":
    # Example image URLs (replace with your own)
    creator = ImageGridCreator(grid_size=(800, 800))
    urls = [
        "https://ae-pic-a1.aliexpress-media.com/kf/Sb1dc4ea309384a7a807cd0a6b8b2f8845.jpg",
        "https://ae-pic-a1.aliexpress-media.com/kf/HTB1mEK0fBUSMeJjy1zjq6A0dXXak.jpg",
        "https://ae-pic-a1.aliexpress-media.com/kf/S808417db5f8249488b13a521d251644bA.jpg",
        "https://ae-pic-a1.aliexpress-media.com/kf/S3f3aceb465a84688889de26fed16989fT.jpeg"
    ]

    result_image = creator.save_grid(urls, r"C:\Users\User\Desktop\images\grid.jpg")

    # Optionally display the image (if running in an environment that supports it)
    # result_image.show()