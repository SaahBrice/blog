import hashlib
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.cache import cache
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

def generate_avatar(username, size=150):
    # Generate a unique color based on the username
    hash_object = hashlib.md5(username.encode())
    hex_dig = hash_object.hexdigest()
    bg_color = f"#{hex_dig[:6]}"

    # Create image
    image = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(image)

    # Calculate font size and get font
    font_size = int(size / 2)
    font = ImageFont.truetype(settings.AVATAR_FONT_PATH, size=font_size)

    # Get initials
    initials = username[:2].upper()

    # Calculate text position
    left, top, right, bottom = font.getbbox(initials)
    text_width = right - left
    text_height = bottom - top
    position = ((size - text_width) / 2, (size - text_height) / 2 - top)

    # Draw text
    draw.text(position, initials, font=font, fill="white")

    # Save image to BytesIO object
    image_io = BytesIO()
    image.save(image_io, format='PNG')

    return ContentFile(image_io.getvalue(), name=f"{username}_avatar.png")

def get_or_create_avatar(user):
    cache_key = f'user_avatar_{user.id}'
    avatar_url = cache.get(cache_key)

    if not avatar_url:
        if not user.profile_picture:
            avatar = generate_avatar(user.username)
            user.profile_picture.save(f"{user.username}_avatar.png", avatar, save=True)
        avatar_url = user.profile_picture.url
        cache.set(cache_key, avatar_url, timeout=86400)  # Cache for 24 hours

    return avatar_url