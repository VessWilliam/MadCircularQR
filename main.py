import qrcode
from PIL import Image, ImageDraw, ImageFont

BOX_SIZE = 12
BORDER = 1
DATA_URL = "https://madteddy-one.vercel.app/StoryBlog"
LOGO_PATH = "logo.ico"
OUTPUT_PATH = "madteddy_with_watermark.png"
LOGO_SIZE = (111, 111)
WATERMARK_TEXT = "Madteddy.co"
WATERMARK_OPACITY = 255  
WATERMARK_FONT_SIZE = 8

# Generate QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=BOX_SIZE,
    border=BORDER,
)
qr.add_data(DATA_URL)
qr.make(fit=True)

# Create blank image for QR code
qr_matrix = qr.modules
qr_size = (len(qr_matrix) + BORDER * 2) * BOX_SIZE
img = Image.new("RGBA", (qr_size, qr_size), "black")
draw = ImageDraw.Draw(img)

FINDER_OUTER = 7 * BOX_SIZE

# draw finder pattern
def draw_finder_pattern(draw, top_left_x, top_left_y):
    offsets = [0, BOX_SIZE, 2 * BOX_SIZE]
    colors = ["yellow", "black", "black"]
    for offset, color in zip(offsets, colors):
        draw.ellipse(
            [
                top_left_x + offset,
                top_left_y + offset,
                top_left_x + FINDER_OUTER - offset,
                top_left_y + FINDER_OUTER - offset,
            ],
            fill=color,
        )

# Draw the three corner finder patterns
corner_positions = [
    (BORDER * BOX_SIZE, BORDER * BOX_SIZE),
    ((len(qr_matrix) - 7 + BORDER) * BOX_SIZE, BORDER * BOX_SIZE),
    (BORDER * BOX_SIZE, (len(qr_matrix) - 7 + BORDER) * BOX_SIZE),
]
for pos in corner_positions:
    draw_finder_pattern(draw, *pos)

# Draw the remaining QR code modules as circular dots
for y, row in enumerate(qr_matrix):
    for x, value in enumerate(row):
        if (x < 7 and y < 7) or (x > len(qr_matrix) - 8 and y < 7) or (x < 7 and y > len(qr_matrix) - 8):
            continue
        if value:
            x0 = (x + BORDER) * BOX_SIZE
            y0 = (y + BORDER) * BOX_SIZE
            x1 = x0 + BOX_SIZE
            y1 = y0 + BOX_SIZE
            draw.ellipse([x0, y0, x1, y1], fill="yellow")


# Overlay logo (cropped to round shape)
overlay_image = Image.open(LOGO_PATH).convert("RGBA").resize(LOGO_SIZE)

# Create a circular mask
mask = Image.new("L", LOGO_SIZE, 0)  # Create a black mask (transparent)
draw_mask = ImageDraw.Draw(mask)

# Draw a white circle on the mask
draw_mask.ellipse((0, 0, LOGO_SIZE[0], LOGO_SIZE[1]), fill=255)

# Apply the mask to the logo image
circular_logo = Image.composite(overlay_image, Image.new(
    "RGBA", LOGO_SIZE, (0, 0, 0, 0)), mask)

# Position for the overlay
overlay_position = (
    (qr_size - LOGO_SIZE[0]) // 2,
    (qr_size - LOGO_SIZE[1]) // 2,
)

# Paste the circular logo onto the QR code
img.paste(circular_logo, overlay_position, circular_logo)

# Add watermark
watermark_font = ImageFont.truetype(
    "arial.ttf", WATERMARK_FONT_SIZE)  
watermark_bbox = draw.textbbox(
    (0, 0), WATERMARK_TEXT, font=watermark_font) 
watermark_width = watermark_bbox[2] - watermark_bbox[0]
watermark_height = watermark_bbox[3] - watermark_bbox[1]
watermark_position = (
    (qr_size - watermark_width) // 35, 
    qr_size - watermark_height - 1.5, 
)
draw.text(
    watermark_position,
    WATERMARK_TEXT,
    fill=(255, 255, 255, WATERMARK_OPACITY),   
    font=watermark_font,
)

img.save(OUTPUT_PATH, "PNG")
