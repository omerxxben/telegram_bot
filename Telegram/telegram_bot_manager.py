import time
from typing import Dict, Any
from io import BytesIO

import pandas as pd
from PIL import Image, ImageDraw
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from Classes.image_grid_creator import ImageGridCreator
from main_actual_code import MainProducts

class TelegramBotManager:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.application = Application.builder().token(bot_token).build()
        self._setup_handlers()

        # Template configuration - centralized for easy updates
        self.template_config = {
            'medal_icons': self._generate_medal_icons(),
            'cart_icon': '🛒',
            'star_icon': '⭐️',
            'money_bag_icon': '💰',
            'link_icon': '🔗',
            'title_line': '[אייקון_מדליה] [שם_מוצר]',
            'sales_line': '[אייקון_עגלה] [כמות_מכירות] רכישות',
            'rating_line': '[אייקון_כוכב] [דירוג] מ-[כמות_ביקורות] ביקורות',
            'price_line': '[אייקון_כסף] מחיר: [מחיר] ₪',
            'link_line': '[אייקון_קישור] [קישור_שותף]',
            'bot_signature': 'שמשון מותגים',
            'search_more_button_text': 'עוד תוצאות 🔍',
            'activation_keywords': ['חפש לי', 'מצא לי'],
            'search_in_process': 'מחפש עבורך... אנא המתן 🔍'
        }

        # Error messages - centralized
        self.error_messages = {
            'no_results': 'מצטערים, לא מצאנו תוצאות עבור \'{}\'.',
            'no_activation': 'לחיפוש, יש להקליד \'חפש לי...\' ואת שם המוצר הרצוי ✨',
            'no_product_name': 'אנא ציין את שם המוצר שברצונך לחפש',
            'unauthorized_click': 'רק מי שביקש את חיפוש זה יכול לבקש עוד מוצרים 😊',
            'invalid_data': 'שגיאה: נתונים לא חוקיים',
            'search_expired': 'שגיאה: החיפוש פג תוקף. אנא בצע חיפוש חדש.',
            'search_exhausted': 'כל המוצרים הזמינים עבור חיפוש זה כבר הוצגו ✅'
        }

    def _generate_medal_icons(self):
        """Generate medal icons for positions 0-49"""
        icons = ['🥇', '🥈', '🥉']  # First 3 positions get medals
        
        # For positions 4-49, create number emojis
        for i in range(4, 50):
            number_str = str(i)
            emoji_number = ''.join([f'{digit}️⃣' for digit in number_str])
            icons.append(emoji_number)
        
        return icons

    def _setup_handlers(self):
        """Setup all bot handlers"""
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))

    def format_product_text(self, product: Dict[str, Any], position: int) -> str:
        """Format a single product using the template system"""
        # Get the appropriate medal icon
        medal_icon = self.template_config['medal_icons'][position] if position < len(
            self.template_config['medal_icons']) else f"{position + 1}️⃣"

        # Format each line separately
        title_line = self.template_config['title_line']
        sales_line = self.template_config['sales_line']
        rating_line = self.template_config['rating_line']
        price_line = self.template_config['price_line']
        link_line = self.template_config['link_line']

        # Replace placeholders in title line
        title_line = title_line.replace('[אייקון_מדליה]', medal_icon)
        title_line = title_line.replace('[שם_מוצר]', product['product_title'])

        # Replace placeholders in sales line
        sales_line = sales_line.replace('[אייקון_עגלה]', self.template_config['cart_icon'])
        sales_line = sales_line.replace('[כמות_מכירות]', str(product['sales_count']))

        # Replace placeholders in rating line
        rating_line = rating_line.replace('[אייקון_כוכב]', self.template_config['star_icon'])
        rating_line = rating_line.replace('[דירוג]', str(product['rating']))
        rating_line = rating_line.replace('[כמות_ביקורות]', str(product['reviews_count']))

        # Replace placeholders in price line
        price_line = price_line.replace('[אייקון_כסף]', self.template_config['money_bag_icon'])
        price_line = price_line.replace('[מחיר]', str(product['price']))

        # Replace placeholders in link line
        link_line = link_line.replace('[אייקון_קישור]', self.template_config['link_icon'])
        link_line = link_line.replace('[קישור_שותף]', product['affiliate_link'])

        # Join all lines with newlines
        formatted_text = '\n'.join([title_line, sales_line, rating_line, price_line, link_line])

        return formatted_text

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages and check for activation keywords"""
        start_time = time.time()
        
        message_text = update.message.text.strip()

        # Check for activation keywords
        activation_found = False
        product_name = ""

        for keyword in self.template_config['activation_keywords']:
            if message_text.startswith(keyword):
                activation_found = True
                product_name = message_text[len(keyword):].strip()
                break

        if not activation_found:
            await update.message.reply_text(self.error_messages['no_activation'])
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"⏱️ Message processing time (no activation): {processing_time:.3f} seconds")
            return

        if not product_name:
            await update.message.reply_text(self.error_messages['no_product_name'])
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"⏱️ Message processing time (no product name): {processing_time:.3f} seconds")
            return

        # Send "search in process" message
        search_message = await update.message.reply_text(self.template_config['search_in_process'])

        # Perform search
        try:
            search_response = MainProducts().process(product_name)

            if not search_response:
                # Delete search message before sending error
                await search_message.delete()
                await update.message.reply_text(self.error_messages['no_results'].format(product_name))
                end_time = time.time()
                processing_time = end_time - start_time
                print(f"⏱️ Message processing time (no results): {processing_time:.3f} seconds")
                return

            # Create unique search ID using timestamp
            search_id = str(int(time.time() * 1000))  # Milliseconds for uniqueness
            
            # Initialize searches dict if it doesn't exist
            if 'searches' not in context.user_data:
                context.user_data['searches'] = {}
            
            # Store search state with unique ID
            context.user_data['searches'][search_id] = {
                'search_response': search_response,
                'original_query': product_name,
                'user_id': update.effective_user.id,
                'timestamp': time.time(),
                'original_message_id': update.message.message_id
            }
            
            # Clean up old searches (keep only last 10)
            if len(context.user_data['searches']) > 10:
                oldest_keys = sorted(context.user_data['searches'].keys())[:-10]
                for old_key in oldest_keys:
                    del context.user_data['searches'][old_key]

            # Delete search message before sending results
            await search_message.delete()

            # Send first page
            await self.send_product_page(update, context, 0, search_id)
            
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"⏱️ Message processing time (successful search): {processing_time:.3f} seconds")

        except Exception as e:
            # Delete search message before sending error
            await search_message.delete()
            await update.message.reply_text("שגיאה בביצוע החיפוש. אנא נסו שוב.")
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"⏱️ Message processing time (error): {processing_time:.3f} seconds")

    async def send_product_page(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page_index: int, search_id: str):
        """Send a page of products (up to 3 products)"""
        # Get search data by ID
        search_data = context.user_data.get('searches', {}).get(search_id)
        if not search_data:
            return
            
        search_response = search_data['search_response']
        products_list = search_response.get('products_list', [])

        # Calculate products for this page
        start_idx = page_index * 3
        end_idx = min(start_idx + 3, len(products_list))
        page_products = products_list[start_idx:end_idx]

        if not page_products:
            return

        # Format caption text
        formatted_products = []
        for i, product in enumerate(page_products):
            actual_position = start_idx + i
            formatted_text = self.format_product_text(product, actual_position)
            formatted_products.append(formatted_text)

        caption = '\n\n\n'.join(formatted_products)
        caption += f'\n\n\n{self.template_config["bot_signature"]}'

        creator = ImageGridCreator(grid_size=(800, 800))
        page_products_pd = pd.DataFrame(page_products)
        image_bytes_io, coshi = creator.save_grid(page_products_pd)

        if not image_bytes_io:
            image_bytes_io = self._create_fallback_image()
        
        # Ensure we're at the beginning of the BytesIO stream
        if hasattr(image_bytes_io, 'seek'):
            image_bytes_io.seek(0)

        # Create keyboard if there are more results
        keyboard = []
        if end_idx < len(products_list):
            next_page = page_index + 1
            user_id = search_data['user_id']
            callback_data = f"nav:{next_page}:{user_id}:{search_id}"

            button = InlineKeyboardButton(
                self.template_config['search_more_button_text'],
                callback_data=callback_data
            )
            keyboard.append([button])
        else:
            # Mark search as exhausted when we reach the last page
            context.user_data['searches'][search_id]['exhausted'] = True

        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        # Get the chat and original message ID for consistent reply threading
        chat_id = update.effective_chat.id
        original_message_id = search_data['original_message_id']

        # Send photo with caption - always reply to original message
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=image_bytes_io,
            caption=caption,
            reply_markup=reply_markup,
            reply_to_message_id=original_message_id
        )

    def _create_fallback_image(self) -> BytesIO:
        """Create a fallback image when base64 image is not available"""
        img = Image.new('RGB', (600, 600), 'lightgray')
        draw = ImageDraw.Draw(img)
        draw.text((300, 300), "תמונה לא זמינה", fill='black', anchor="mm")

        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboard buttons"""
        start_time = time.time()
        
        query = update.callback_query

        try:
            # Parse callback data
            data_parts = query.data.split(':')
            
            if len(data_parts) != 4 or data_parts[0] != 'nav':
                await query.answer(self.error_messages['invalid_data'], show_alert=True)
                end_time = time.time()
                processing_time = end_time - start_time
                print(f"⏱️ Callback processing time (invalid data): {processing_time:.3f} seconds")
                return

            target_page = int(data_parts[1])
            original_user_id = int(data_parts[2])
            search_id = data_parts[3]

            # Check if current user is authorized
            if update.effective_user.id != original_user_id:
                await query.answer(self.error_messages['unauthorized_click'], show_alert=True)
                end_time = time.time()
                processing_time = end_time - start_time
                print(f"⏱️ Callback processing time (unauthorized): {processing_time:.3f} seconds")
                return

            # Check if search state exists
            search_data = context.user_data.get('searches', {}).get(search_id)
            if not search_data:
                await query.answer(self.error_messages['search_expired'], show_alert=True)
                end_time = time.time()
                processing_time = end_time - start_time
                print(f"⏱️ Callback processing time (expired): {processing_time:.3f} seconds")
                return

            # Check if search is exhausted (all products already shown)
            if search_data.get('exhausted', False):
                await query.answer(self.error_messages['search_exhausted'], show_alert=True)
                end_time = time.time()
                processing_time = end_time - start_time
                print(f"⏱️ Callback processing time (exhausted): {processing_time:.3f} seconds")
                return

            products_list = search_data['search_response'].get('products_list', [])

            # Send the requested page
            await self.send_product_page(update, context, target_page, search_id)
            
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"⏱️ Callback processing time (successful): {processing_time:.3f} seconds")

        except (ValueError, IndexError) as e:
            await query.answer(self.error_messages['invalid_data'], show_alert=True)
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"⏱️ Callback processing time (value/index error): {processing_time:.3f} seconds")
        except Exception as e:
            await query.answer("שגיאה לא צפויה", show_alert=True)
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"⏱️ Callback processing time (unexpected error): {processing_time:.3f} seconds")

    def run(self):
        """Start the bot"""
        self.application.run_polling()