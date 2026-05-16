# app/utils/image_utils.py
import base64
import io
import numpy as np
from PIL import Image
import aiohttp
import cv2
from typing import Union


async def load_image(source: Union[str, bytes]) -> np.ndarray:
    """Загрузка изображения из различных источников"""

    if isinstance(source, bytes):
        # Загрузка из байтов
        image = Image.open(io.BytesIO(source))
        return np.array(image)

    elif isinstance(source, str):
        if source.startswith(('http://', 'https://')):
            # Загрузка по URL
            async with aiohttp.ClientSession() as session:
                async with session.get(source) as response:
                    data = await response.read()
                    image = Image.open(io.BytesIO(data))
                    return np.array(image)

        elif source.startswith('data:image'):
            # Загрузка из base64 data URL
            header, encoded = source.split(',', 1)
            data = base64.b64decode(encoded)
            image = Image.open(io.BytesIO(data))
            return np.array(image)

        else:
            # Загрузка из файла
            image = Image.open(source)
            return np.array(image)

    raise ValueError(f"Unsupported image source type: {type(source)}")


def preprocess_image(
        image: np.ndarray,
        target_size: tuple = (640, 640),
        normalize: bool = True
) -> np.ndarray:
    """Предобработка изображения"""

    # Ресайз
    image = cv2.resize(image, target_size)

    # Нормализация
    if normalize:
        image = image.astype(np.float32) / 255.0

    return image


def postprocess_predictions(
        predictions: list,
        original_size: tuple,
        target_size: tuple
) -> list:
    """Постобработка предсказаний с приведением к оригинальному размеру"""

    scale_x = original_size[1] / target_size[1]
    scale_y = original_size[0] / target_size[0]

    processed = []
    for pred in predictions:
        if pred.get('bbox'):
            pred['bbox'] = [
                pred['bbox'][0] * scale_x,
                pred['bbox'][1] * scale_y,
                pred['bbox'][2] * scale_x,
                pred['bbox'][3] * scale_y
            ]
        processed.append(pred)

    return processed