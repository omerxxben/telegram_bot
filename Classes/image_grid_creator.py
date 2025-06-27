import base64

import pandas as pd
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
        self.medal_emojis = {
            1: '🥇',  # Gold medal
            2: '🥈',  # Silver medal
            3: '🥉',  # Bronze medal
            4: '🏅'  # Sports medal for 4th place
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

    def create_medal(self, place: int, size: int = 80) -> Image.Image:
        """
        Create a medal emoji image for the given place (or number for 4th place)

        Args:
            place: Place number (1-4)
            size: Size of the medal in pixels

        Returns:
            PIL Image object of the medal emoji or number
        """
        medal = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(medal)

        if place == 4:
            # For 4th place, draw a smaller circle with the number 4
            circle_margin = 15  # More margin to make circle smaller
            draw.ellipse([circle_margin, circle_margin, size - circle_margin, size - circle_margin], fill='#4A4A4A',
                         outline='black', width=2)

            # Add the number 4 with Rubik font (smaller size)
            try:
                font = ImageFont.truetype("Rubik-Regular.ttf", size // 3)  # Smaller font
            except:
                try:
                    font = ImageFont.truetype("Rubik.ttf", size // 3)
                except:
                    try:
                        # Try system font paths
                        font = ImageFont.truetype("C:/Windows/Fonts/Rubik-Regular.ttf", size // 3)
                    except:
                        # Fall back to arial if Rubik not found
                        try:
                            font = ImageFont.truetype("arial.ttf", size // 3)
                        except:
                            font = ImageFont.load_default()

            text = "4"
            # Get exact text bounding box for perfect centering
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Calculate center position more precisely
            x = (size - text_width) // 2 - bbox[0]  # Adjust for bbox offset
            y = (size - text_height) // 2 - bbox[1]  # Adjust for bbox offset

            draw.text((x, y), text, fill='white', font=font, stroke_width=2, stroke_fill='black')
        else:
            # For 1st, 2nd, 3rd place, use emojis
            emoji = self.medal_emojis.get(place, '🏅')

            # Try to use a larger font size for better emoji visibility
            font_size = int(size * 0.8)  # Use 80% of the medal size
            try:
                # Try to load a font that supports emojis
                font = ImageFont.truetype("seguiemj.ttf", font_size)  # Windows emoji font
            except:
                try:
                    font = ImageFont.truetype("NotoColorEmoji.ttf", font_size)  # Linux emoji font
                except:
                    try:
                        font = ImageFont.truetype("Apple Color Emoji.ttc", font_size)  # macOS emoji font
                    except:
                        # Fall back to default font with smaller size
                        font = ImageFont.load_default()
                        font_size = size // 2

            # Draw the emoji
            bbox = draw.textbbox((0, 0), emoji, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            draw.text((x, y), emoji, font=font, embedded_color=True)

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
        num_images = len(image_urls)

        # 1 image case: unchanged
        if num_images == 1:
            # same as before...
            img = self.download_image(image_urls[0])
            img = self.resize_image_to_fit(img, self.grid_size)
            grid_image = Image.new('RGB', self.grid_size, 'white')
            grid_image.paste(img, (0, 0))
            medal = self.create_medal(1, size=100)
            medal_x = self.grid_size[0] - medal.width - 20
            medal_y = 20
            if medal.mode == 'RGBA':
                grid_image.paste(medal, (medal_x, medal_y), medal)
            else:
                grid_image.paste(medal, (medal_x, medal_y))
            return grid_image

        # 2 images case: unchanged, but swap positions (1st right, 2nd left) with medals top-right with padding 20px
        if num_images == 2:
            individual_size = (self.grid_size[0] // 2, self.grid_size[1])

            images = []
            for url in image_urls:
                img = self.download_image(url)
                img = self.resize_image_to_fit(img, individual_size)
                images.append(img)

            grid_image = Image.new('RGB', self.grid_size, 'white')

            # Positions: 1st place right, 2nd place left
            positions = [
                (self.grid_size[0] // 2, 0),  # 1st place - right half
                (0, 0),  # 2nd place - left half
            ]

            for i, (img, pos) in enumerate(zip(images, positions)):
                grid_image.paste(img, pos)
                medal = self.create_medal(i + 1, size=80)

                # Medal position:
                # X = image right edge - medal width - 20 px padding
                medal_x = pos[0] + individual_size[0] - medal.width - 20

                # Y = image top + 20 px padding
                medal_y = pos[1] + 200

                if medal.mode == 'RGBA':
                    grid_image.paste(medal, (medal_x, medal_y), medal)
                else:
                    grid_image.paste(medal, (medal_x, medal_y))

            return grid_image

        # 3 images case: first two on top row (half width each), third centered on bottom row
        if num_images == 3:
            half_width = self.grid_size[0] // 2
            half_height = self.grid_size[1] // 2

            # Sizes
            top_size = (half_width, half_height)
            bottom_size = (half_width, half_height)  # You can adjust width here if you want narrower bottom image

            # Download and resize images
            images = []
            for idx, url in enumerate(image_urls):
                size = top_size if idx < 2 else bottom_size
                img = self.download_image(url)
                img = self.resize_image_to_fit(img, size)
                images.append(img)

            grid_image = Image.new('RGB', self.grid_size, 'white')

            # Positions:
            positions = [
                (half_width, 0),  # 1st place - top right
                (0, 0),  # 2nd place - top left
                ((self.grid_size[0] - bottom_size[0]) // 2, half_height),  # 3rd place - centered bottom
            ]

            for i, (img, pos) in enumerate(zip(images, positions)):
                grid_image.paste(img, pos)
                medal = self.create_medal(i + 1, size=80)
                medal_x = pos[0] + img.width - medal.width - 20
                medal_y = pos[1] + 20
                if medal.mode == 'RGBA':
                    grid_image.paste(medal, (medal_x, medal_y), medal)
                else:
                    grid_image.paste(medal, (medal_x, medal_y))

            return grid_image

        # 4 images case: default 2x2 grid as before
        image_urls = image_urls[:4] + [None] * (4 - len(image_urls))

        individual_width = self.grid_size[0] // 2
        individual_height = self.grid_size[1] // 2
        individual_size = (individual_width, individual_height)

        images = []
        for url in image_urls:
            if url:
                img = self.download_image(url)
            else:
                img = Image.new('RGB', (400, 300), color='lightgray')
                draw = ImageDraw.Draw(img)
                draw.text((200, 150), "No Image", fill='black', anchor='mm')
            img = self.resize_image_to_fit(img, individual_size)
            images.append(img)

        grid_image = Image.new('RGB', self.grid_size, 'white')

        positions = [
            (individual_width, 0),  # Top right (1st place)
            (0, 0),  # Top left (2nd place)
            (individual_width, individual_height),  # Bottom right (3rd place)
            (0, individual_height)  # Bottom left (4th place)
        ]

        for i, (img, pos) in enumerate(zip(images, positions)):
            grid_image.paste(img, pos)
            medal = self.create_medal(i + 1, size=80)
            medal_x = pos[0] + individual_width - medal.width - 20
            medal_y = pos[1] + 20
            if medal.mode == 'RGBA':
                grid_image.paste(medal, (medal_x, medal_y), medal)
            else:
                grid_image.paste(medal, (medal_x, medal_y))

        return grid_image

    def save_grid(self, df: pd.DataFrame,
                  image_column: str = "product_main_image_url"):
        if df.empty:
            default_url = "https://cloudinary-marketing-res.cloudinary.com/images/w_1000,c_scale/v1679921049/Image_URL_header/Image_URL_header-png?_i=AA"
            default_image = self.download_image(default_url)
            return self.pil_image_to_base64_str(default_image)
        image_urls = df[image_column].dropna().head(4).tolist()
        grid_image = self.create_grid(image_urls)
        return self.pil_image_to_bytesio(grid_image)

    def pil_image_to_bytesio(self, pil_img: Image.Image, format: str = "PNG") -> io.BytesIO:
        buffered = io.BytesIO()
        buffered.name = f'image.{format.lower()}'
        pil_img.save(buffered, format=format)
        buffered.seek(0)
        return buffered
