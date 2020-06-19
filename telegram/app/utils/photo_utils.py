import random

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import List, Union

__all__ = ('prepare_photo',)


def prepare_photo(image_data: Union[bytes, BytesIO], faces: List[dict]) -> BytesIO:
    if isinstance(image_data, bytes):
        image_data = BytesIO(image_data)
    image = Image.open(image_data)

    watermark_size = image.size[0] // 6, image.size[1] // 6
    watermark_position = int(image.size[0] - watermark_size[0] * 1.5), \
        int(watermark_size[1] * 0.5)
    watermark = Image.open('./watermark.png')
    watermark.thumbnail(watermark_size, Image.ANTIALIAS)
    image.paste(watermark, watermark_position, watermark)

    draw = ImageDraw.Draw(image)

    for face in faces:
        cords: list = face["cords"]
        prediction: str = face["prediction"]

        if face["accuracy"] < 0.6:
            color = "#FFA000"
        elif prediction == "straight":
            color = "#4CAF50"
        else:
            color = "#FF5722"

        max_size = max(cords[2] - cords[0], cords[3] - cords[1])
        draw.rectangle(
            ((cords[0], cords[1]), (cords[2], cords[3])),
            outline=color,
            width=max_size // 100 if max_size > 100 else 1,
        )

        max_height = (cords[3] - cords[1]) // 5
        max_width = cords[2] - cords[0]

        description = f'{prediction.upper()} {int(round(face["accuracy"] * 100, 2))}%'

        font_size = 1
        font = ImageFont.truetype("./jetbrains-mono.ttf", size=font_size)
        while True:
            description_size = font.getsize(description)
            if (
                description_size[1] > max_height * 0.8
                or int(description_size[0] * 1.1) > max_width
            ):
                font_size -= 1
                font = ImageFont.truetype("./jetbrains-mono.ttf", size=font_size)
                description_size = font.getsize(description)
                break
            font_size += 1
            font = ImageFont.truetype("./jetbrains-mono.ttf", size=font_size)

        label_cords = (
            (cords[0], cords[1] - description_size[1] - max_height // 5),
            (cords[0] + int(description_size[0] * 1.1), cords[1]),
        )

        draw.rectangle(
            label_cords, fill=color
        )

        draw.text(
            (
                label_cords[0][0] + int(description_size[0] * 0.05),
                label_cords[0][1] + max_height * 0.1 - description_size[1] // 8,
            ),
            description,
            font=font,
        )

    result = BytesIO()
    image.save(result, format='PNG')
    result.seek(0)
    return result
