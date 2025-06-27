import base64

import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
        # Modern color scheme
        self.colors = {
            'primary': '#1a1a1a',  # Dark charcoal
            'secondary': '#2d2d2d',  # Medium gray
            'accent': '#4a9eff',  # Modern blue
            'light': '#f8f9fa',  # Off-white
            'gradient_start': '#667eea',  # Purple-blue
            'gradient_end': '#764ba2',  # Purple
            'shadow': '#00000020'  # Transparent black for shadows
        }

    def create_modern_background(self, size: Tuple[int, int]) -> Image.Image:
        """
        Create a modern gradient background with subtle pattern

        Args:
            size: Size of the background image

        Returns:
            PIL Image with modern background
        """
        width, height = size
        background = Image.new('RGB', size, self.colors['primary'])

        # Create gradient overlay
        gradient = Image.new('RGB', size, self.colors['gradient_start'])
        gradient_draw = ImageDraw.Draw(gradient)

        # Create diagonal gradient
        for i in range(width):
            # Calculate gradient position (0 to 1)
            pos = i / width
            # Interpolate between gradient colors
            r1, g1, b1 = tuple(int(self.colors['gradient_start'][i:i + 2], 16) for i in (1, 3, 5))
            r2, g2, b2 = tuple(int(self.colors['gradient_end'][i:i + 2], 16) for i in (1, 3, 5))

            r = int(r1 + (r2 - r1) * pos)
            g = int(g1 + (g2 - g1) * pos)
            b = int(b1 + (b2 - b1) * pos)

            gradient_draw.line([(i, 0), (i, height)], fill=(r, g, b))

        # Blend gradient with background
        background = Image.blend(background, gradient, 0.7)

        # Add subtle geometric pattern
        pattern_draw = ImageDraw.Draw(background)

        # Add diagonal lines pattern
        for i in range(0, width + height, 40):
            pattern_draw.line([(i, 0), (i - height, height)], fill=self.colors['secondary'], width=1)

        return background

    def create_image_frame(self, image: Image.Image, frame_size: Tuple[int, int],
                           corner_radius: int = 15, shadow_offset: int = 8) -> Image.Image:
        """
        Create a modern frame around an image with rounded corners and shadow

        Args:
            image: PIL Image to frame
            frame_size: Size of the frame area
            corner_radius: Radius for rounded corners
            shadow_offset: Offset for drop shadow

        Returns:
            PIL Image with modern frame
        """
        # Create frame with padding
        padding = 20
        inner_size = (frame_size[0] - 2 * padding, frame_size[1] - 2 * padding)

        # Resize image to fit inner area
        image.thumbnail(inner_size, Image.Resampling.LANCZOS)

        # Create frame background
        frame = Image.new('RGBA', frame_size, (0, 0, 0, 0))
        frame_draw = ImageDraw.Draw(frame)

        # Calculate centered position for image
        img_x = (frame_size[0] - image.width) // 2
        img_y = (frame_size[1] - image.height) // 2

        # Create shadow
        shadow_color = self.colors['shadow']
        shadow_x = img_x + shadow_offset
        shadow_y = img_y + shadow_offset

        # Draw shadow rectangle with rounded corners
        frame_draw.rounded_rectangle(
            [shadow_x, shadow_y, shadow_x + image.width, shadow_y + image.height],
            radius=corner_radius,
            fill=shadow_color
        )

        # Create white background for image with rounded corners
        frame_draw.rounded_rectangle(
            [img_x - 5, img_y - 5, img_x + image.width + 5, img_y + image.height + 5],
            radius=corner_radius,
            fill='white',
            outline=self.colors['accent'],
            width=2
        )

        # Convert image to RGBA if needed
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Create rounded mask for image
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, image.width, image.height], radius=corner_radius, fill=255)

        # Apply mask to image
        masked_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
        masked_image.paste(image, (0, 0))
        masked_image.putalpha(mask)

        # Paste masked image onto frame
        frame.paste(masked_image, (img_x, img_y), masked_image)

        return frame

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
            # Create a modern placeholder image if download fails
            placeholder = Image.new('RGB', (400, 300), color=self.colors['light'])
            draw = ImageDraw.Draw(placeholder)

            # Add modern placeholder design
            draw.rounded_rectangle([20, 20, 380, 280], radius=20, fill=self.colors['secondary'])
            draw.text((200, 150), "Image Not Found", fill=self.colors['light'], anchor='mm')

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
            # For 4th place, draw a circle with the number 4
            circle_margin = 15
            draw.ellipse([circle_margin, circle_margin, size - circle_margin, size - circle_margin],
                         fill='#4A4A4A', outline='black', width=2)

            # Add the number 4
            try:
                font = ImageFont.truetype("Rubik-Regular.ttf", size // 3)
            except:
                try:
                    font = ImageFont.truetype("Rubik.ttf", size // 3)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/Rubik-Regular.ttf", size // 3)
                    except:
                        try:
                            font = ImageFont.truetype("arial.ttf", size // 3)
                        except:
                            font = ImageFont.load_default()

            text = "4"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (size - text_width) // 2 - bbox[0]
            y = (size - text_height) // 2 - bbox[1]

            draw.text((x, y), text, fill='white', font=font, stroke_width=2, stroke_fill='black')
        else:
            # For 1st, 2nd, 3rd place, use emojis only
            emoji = self.medal_emojis.get(place, '🏅')

            font_size = int(size * 0.8)
            try:
                font = ImageFont.truetype("seguiemj.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("NotoColorEmoji.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("Apple Color Emoji.ttc", font_size)
                    except:
                        font = ImageFont.load_default()
                        font_size = size // 2

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
        return image

    def create_grid(self, image_urls: List[str]) -> Image.Image:
        num_images = len(image_urls)

        # Create modern background
        grid_image = self.create_modern_background(self.grid_size)

        # 1 image case
        if num_images == 1:
            img = self.download_image(image_urls[0])
            framed_img = self.create_image_frame(img, self.grid_size, corner_radius=20)

            # Convert to RGB for final composition
            final_grid = Image.new('RGB', self.grid_size, self.colors['primary'])
            final_grid.paste(grid_image, (0, 0))
            if framed_img.mode == 'RGBA':
                final_grid.paste(framed_img, (0, 0), framed_img)
            else:
                final_grid.paste(framed_img, (0, 0))

            # Add medal
            medal = self.create_medal(1, size=100)
            medal_x = self.grid_size[0] - medal.width - 5
            medal_y = 10
            if medal.mode == 'RGBA':
                final_grid.paste(medal, (medal_x, medal_y), medal)
            else:
                final_grid.paste(medal, (medal_x, medal_y))

            return final_grid

        # 2 images case
        if num_images == 2:
            individual_size = (self.grid_size[0] // 2, self.grid_size[1])

            final_grid = Image.new('RGB', self.grid_size, self.colors['primary'])
            final_grid.paste(grid_image, (0, 0))

            images = []
            for url in image_urls:
                img = self.download_image(url)
                framed_img = self.create_image_frame(img, individual_size, corner_radius=15)
                images.append(framed_img)

            # Positions: 1st place right, 2nd place left
            positions = [
                (self.grid_size[0] // 2, 0),  # 1st place - right half
                (0, 0),  # 2nd place - left half
            ]

            for i, (img, pos) in enumerate(zip(images, positions)):
                if img.mode == 'RGBA':
                    final_grid.paste(img, pos, img)
                else:
                    final_grid.paste(img, pos)

                medal = self.create_medal(i + 1, size=80)
                medal_x = pos[0] + individual_size[0] - medal.width - 5
                medal_y = pos[1] + 10

                if medal.mode == 'RGBA':
                    final_grid.paste(medal, (medal_x, medal_y), medal)
                else:
                    final_grid.paste(medal, (medal_x, medal_y))

            return final_grid

        # 3 images case
        if num_images == 3:
            half_width = self.grid_size[0] // 2
            half_height = self.grid_size[1] // 2
            top_size = (half_width, half_height)
            bottom_size = (half_width, half_height)

            final_grid = Image.new('RGB', self.grid_size, self.colors['primary'])
            final_grid.paste(grid_image, (0, 0))

            images = []
            for idx, url in enumerate(image_urls):
                size = top_size if idx < 2 else bottom_size
                img = self.download_image(url)
                framed_img = self.create_image_frame(img, size, corner_radius=15)
                images.append(framed_img)

            positions = [
                (half_width, 0),  # 1st place - top right
                (0, 0),  # 2nd place - top left
                ((self.grid_size[0] - bottom_size[0]) // 2, half_height),  # 3rd place - centered bottom
            ]

            for i, (img, pos) in enumerate(zip(images, positions)):
                if img.mode == 'RGBA':
                    final_grid.paste(img, pos, img)
                else:
                    final_grid.paste(img, pos)

                medal = self.create_medal(i + 1, size=80)
                medal_x = pos[0] + img.width - medal.width - 30
                medal_y = pos[1] + 30

                if medal.mode == 'RGBA':
                    final_grid.paste(medal, (medal_x, medal_y), medal)
                else:
                    final_grid.paste(medal, (medal_x, medal_y))

            return final_grid

        # 4 images case
        image_urls = image_urls[:4] + [None] * (4 - len(image_urls))
        individual_width = self.grid_size[0] // 2
        individual_height = self.grid_size[1] // 2
        individual_size = (individual_width, individual_height)

        final_grid = Image.new('RGB', self.grid_size, self.colors['primary'])
        final_grid.paste(grid_image, (0, 0))

        images = []
        for url in image_urls:
            if url:
                img = self.download_image(url)
            else:
                img = Image.new('RGB', (400, 300), color=self.colors['light'])
                draw = ImageDraw.Draw(img)
                draw.rounded_rectangle([20, 20, 380, 280], radius=20, fill=self.colors['secondary'])
                draw.text((200, 150), "No Image", fill=self.colors['light'], anchor='mm')

            framed_img = self.create_image_frame(img, individual_size, corner_radius=15)
            images.append(framed_img)

        positions = [
            (individual_width, 0),  # Top right (1st place)
            (0, 0),  # Top left (2nd place)
            (individual_width, individual_height),  # Bottom right (3rd place)
            (0, individual_height)  # Bottom left (4th place)
        ]

        for i, (img, pos) in enumerate(zip(images, positions)):
            if img.mode == 'RGBA':
                final_grid.paste(img, pos, img)
            else:
                final_grid.paste(img, pos)

            medal = self.create_medal(i + 1, size=80)
            medal_x = pos[0] + individual_width - medal.width - 30
            medal_y = pos[1] + 30

            if medal.mode == 'RGBA':
                final_grid.paste(medal, (medal_x, medal_y), medal)
            else:
                final_grid.paste(medal, (medal_x, medal_y))

        return final_grid

    def save_grid(self, df: pd.DataFrame, IS_PRINT_IMAGE=False):
        image_column: str = "product_main_image_url"
        if df.empty:
            default_url = "https://cloudinary-marketing-res.cloudinary.com/images/w_1000,c_scale/v1679921049/Image_URL_header/Image_URL_header-png?_i=AA"
            default_image = self.download_image(default_url)
            return self.pil_image_to_base64_str(default_image)
        image_urls = df[image_column].dropna().head(4).tolist()
        grid_image = self.create_grid(image_urls)
        image_bytes_io = self.pil_image_to_bytesio(grid_image)
        if IS_PRINT_IMAGE:
            image = Image.open(image_bytes_io)
            image.show()
        return image_bytes_io

    def pil_image_to_bytesio(self, pil_img: Image.Image, format: str = "PNG") -> io.BytesIO:
        buffered = io.BytesIO()
        buffered.name = f'image.{format.lower()}'
        pil_img.save(buffered, format=format)
        buffered.seek(0)
        return buffered