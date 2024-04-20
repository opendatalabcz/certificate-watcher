from PIL import Image


def convert_image_to_rgb_with_white_bg(image: Image) -> Image:
    image_format = image.format
    white_bg = Image.new("RGB", image.size, "WHITE")
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        white_bg.paste(image.convert("RGBA"), (0, 0), image.convert("RGBA"))
    else:
        white_bg.paste(image.convert("RGB"))
    white_bg.format = image_format
    return white_bg
