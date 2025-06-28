import base64
import time

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
        }
        # Modern color scheme
        self.colors = {
            'primary': '#1a1a1a',  # Dark charcoal
            'secondary': '#2d2d2d',  # Medium gray
            'accent': '#8394a8',  # Modern blue
            'light': '#f8f9fa',  # Off-white
            'gradient_start': '#667eea',  # Purple-blue
            'gradient_end': '#764ba2',  # Purple
            'shadow': '#00000020'  # Transparent black for shadows
        }

    def create_modern_background(self, size: Tuple[int, int]) -> Image.Image:
        try:
            # Assuming "Classes/background.png" is a valid path
            background = Image.open("Classes/background.png").convert("RGB")
            background = background.resize(size, Image.Resampling.LANCZOS)
            return background
        except Exception as e:
            print(f"Error loading custom background image: {e}. Using fallback.")
            fallback = Image.new('RGB', size, self.colors['primary'])
            return fallback

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
        padding = 20
        inner_size = (frame_size[0] - 2 * padding, frame_size[1] - 2 * padding)
        image.thumbnail(inner_size, Image.Resampling.LANCZOS)
        frame = Image.new('RGBA', frame_size, (0, 0, 0, 0))
        frame_draw = ImageDraw.Draw(frame)
        img_x = (frame_size[0] - image.width) // 2
        img_y = (frame_size[1] - image.height) // 2
        shadow_color = self.colors['shadow']
        shadow_x = img_x + shadow_offset
        shadow_y = img_y + shadow_offset
        frame_draw.rounded_rectangle(
            [shadow_x, shadow_y, shadow_x + image.width, shadow_y + image.height],
            radius=corner_radius,
            fill=shadow_color
        )
        frame_draw.rounded_rectangle(
            [img_x - 5, img_y - 5, img_x + image.width + 5, img_y + image.height + 5],
            radius=corner_radius,
            fill='white',
            outline=self.colors['accent'],
            width=2
        )
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, image.width, image.height], radius=corner_radius, fill=255)
        masked_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
        masked_image.paste(image, (0, 0))
        masked_image.putalpha(mask)
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
            placeholder = Image.new('RGB', (400, 300), color=self.colors['light'])
            draw = ImageDraw.Draw(placeholder)
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            draw.rounded_rectangle([20, 20, 380, 280], radius=20, fill=self.colors['secondary'])
            draw.text((200, 150), "Image Not Found", fill=self.colors['light'], anchor='mm', font=font)
            return placeholder

    def create_medal_or_number(self, ranking: int, size: int = 80) -> Image.Image:
        """
        Create a medal emoji for top 3 positions or a custom-drawn number icon for 4+.

        Args:
            ranking: The actual ranking position (1, 2, 3 for medals, 4+ for numbers)
            size: Size of the medal/number icon in pixels

        Returns:
            PIL Image object of the medal emoji or number icon.
        """
        # Create a transparent canvas for our icon
        icon_image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon_image)

        # For 1st, 2nd, 3rd place, use reliable medal emojis
        if ranking <= 3:
            emoji = self.medal_emojis.get(ranking, '🏅')
            font_size = int(size * 0.8)

            # Try to find a suitable emoji font
            emoji_fonts = [
                "C:/Windows/Fonts/seguiemj.ttf", "seguiemj.ttf",
                "/System/Library/Fonts/Apple Color Emoji.ttc", "Apple Color Emoji.ttc",
                "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", "NotoColorEmoji.ttf"
            ]
            font = None
            for font_path in emoji_fonts:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    # Check if font can actually render the emoji
                    if font.getlength(emoji) > 0:
                        break
                except IOError:
                    continue

            if font:
                try:
                    # Center the emoji on the canvas
                    bbox = draw.textbbox((0, 0), emoji, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = (size - text_width) / 2
                    y = (size - text_height) / 2
                    # Draw the emoji with its embedded color
                    draw.text((x, y), emoji, font=font, embedded_color=True)
                    return icon_image
                except Exception:
                    # Fallback to text if emoji drawing fails
                    pass

        # --- NEW ROBUST METHOD FOR RANK 4+ (and as a fallback for medals) ---
        # For 4th place and beyond, draw the number manually.
        text = str(ranking)

        # Load a standard, reliable font like Arial.
        try:
            # Adjust font size based on number of digits for a better fit
            if len(text) == 1:
                font_size = size // 2
            elif len(text) == 2:
                font_size = size // 2 - 10
            else:  # 3+ digits
                font_size = size // 3
            font = ImageFont.truetype("arialbd.ttf", font_size)  # Bold Arial
        except IOError:
            font = ImageFont.load_default()

        # Draw a modern circular background for the number
        margin = 5  # Small margin around the circle
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=self.colors['accent'],
            width=3
        )

        # Draw the number, centered within the circle
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (size - text_width) // 2 - text_bbox[0]
        y = (size - text_height) // 2 - text_bbox[1]

        # Draw the number with a subtle shadow for better readability
        draw.text((x + 1, y + 1), text, font=font, fill='black')  # Shadow
        draw.text((x, y), text, font=font, fill=self.colors['light'])  # Main text

        return icon_image

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

    def create_grid(self, image_urls: List[str], page_index: int = 0, products_per_page: int = 3) -> Image.Image:
        """
        Create a grid of images with appropriate medals/numbers based on page index

        Args:
            image_urls: List of image URLs
            page_index: Current page index (0-based)
            products_per_page: Number of products per page
        """
        num_images = len(image_urls)
        start_ranking = page_index * products_per_page + 1
        grid_image = self.create_modern_background(self.grid_size)

        if num_images == 0:
            return grid_image  # Return background if no images

        # 1 image case
        if num_images == 1:
            img = self.download_image(image_urls[0])
            framed_img = self.create_image_frame(img, self.grid_size, corner_radius=20)
            final_grid = Image.new('RGB', self.grid_size)
            final_grid.paste(grid_image, (0, 0))
            final_grid.paste(framed_img, (0, 0), framed_img)
            ranking = start_ranking
            medal = self.create_medal_or_number(ranking, size=100)
            medal_x = self.grid_size[0] - medal.width - 20
            medal_y = 25
            final_grid.paste(medal, (medal_x, medal_y), medal)
            return final_grid

        # 2 images case
        if num_images == 2:
            individual_size = (self.grid_size[0] // 2, self.grid_size[1])
            final_grid = Image.new('RGB', self.grid_size)
            final_grid.paste(grid_image, (0, 0))
            for i, url in enumerate(image_urls):
                img = self.download_image(url)
                framed_img = self.create_image_frame(img, individual_size, corner_radius=15)
                # Position right-to-left: First image (higher rank) goes right
                pos = ((1 - i) * (self.grid_size[0] // 2), 0)
                final_grid.paste(framed_img, pos, framed_img)
                ranking = start_ranking + i
                medal = self.create_medal_or_number(ranking, size=80)
                # Adjust medal position based on frame
                if page_index == 0:
                    medal_x = pos[0] + individual_size[0] - medal.width - 20
                    medal_y = pos[1] + 225
                else:
                    medal_x = pos[0] + individual_size[0] - medal.width - 20
                    medal_y = 220
                final_grid.paste(medal, (medal_x, medal_y), medal)
            return final_grid

        # 3 images case
        else:
            half_width = self.grid_size[0] // 2
            half_height = self.grid_size[1] // 2
            final_grid = Image.new('RGB', self.grid_size)
            final_grid.paste(grid_image, (0, 0))

            # Define positions based on ranking (1st top-right, 2nd top-left, 3rd bottom-center)
            positions_and_sizes = [
                ((half_width, 0), (half_width, half_height)),  # Rank 1
                ((0, 0), (half_width, half_height)),  # Rank 2
                ((self.grid_size[0] // 4, half_height), (half_width, half_height)),  # Rank 3
            ]

            for i, url in enumerate(image_urls):
                if i >= len(positions_and_sizes): break  # Safety break

                pos, size = positions_and_sizes[i]
                img = self.download_image(url)
                framed_img = self.create_image_frame(img, size, corner_radius=15)
                final_grid.paste(framed_img, pos, framed_img)

                ranking = start_ranking + i
                medal = self.create_medal_or_number(ranking, size=80)
                if page_index == 0:
                    medal_x = pos[0] + size[0] - medal.width - 20
                    medal_y = pos[1] + 25
                else:
                    medal_x = pos[0] + size[0] - medal.width - 20
                    medal_y = pos[1] + 20
                final_grid.paste(medal, (medal_x, medal_y), medal)

            return final_grid

    def save_grid(self, df: pd.DataFrame, page_index, IS_PRINT_IMAGE=False, products_per_page: int = 3):
        start_time = time.time()
        image_column: str = "product_main_image_url"
        image_urls = df[image_column].dropna().head(products_per_page).tolist()
        grid_image = self.create_grid(image_urls, page_index, products_per_page)
        image_bytes_io = self.pil_image_to_bytesio(grid_image)
        if IS_PRINT_IMAGE:
            image = Image.open(image_bytes_io)
            image.show()
        total_time = time.time() - start_time
        return image_bytes_io, total_time

    def pil_image_to_bytesio(self, pil_img: Image.Image, format: str = "PNG") -> io.BytesIO:
        buffered = io.BytesIO()
        buffered.name = f'image.{format.lower()}'
        pil_img.save(buffered, format=format)
        buffered.seek(0)
        return buffered