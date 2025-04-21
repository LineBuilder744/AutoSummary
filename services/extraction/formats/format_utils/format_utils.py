
async def convert_uploadfile_to_pil_image(upload_file: UploadFile) -> Image.Image:
    # Чтение байтов из файла
    contents = await upload_file.read()
    # Создание объекта BytesIO из байтов
    image_stream = io.BytesIO(contents)

    pil_image = Image.open(image_stream)
    pil_image.load()
    
    return pil_image


def convert_pdf_to_images(
    pdf_bytes: bytes,
    dpi: int = 200,
    first_page: Optional[int] = None,
    last_page: Optional[int] = None,
    fmt: str = 'jpeg',
    thread_count: int = 4
) -> List[Image.Image]:
    try:
        images = convert_from_bytes(
            pdf_bytes,
            dpi=dpi,
            first_page=first_page,
            last_page=last_page,
            fmt=fmt,
            thread_count=thread_count,
            use_pdftocairo=True,
            transparent=False
        )
        
        # Конвертируем в RGB, если нужно (для JPEG)
        if fmt.lower() == 'jpeg':
            images = [image.convert('RGB') for image in images]
            
        return images
        
    except Exception as e:
        raise ValueError(f"Ошибка конвертации PDF: {str(e)}")


def get_png_payload(prompt: str, images: List[Image.Image]) -> List[Union[str, Image.Image]]:
    contents = [prompt]
    contents.extend(images)
    return contents

def get_pdf_payload(prompt: str, pdf_bytes: bytes) -> list:
    contents = [prompt, pdf_bytes]
    
    return contents


