import zipfile
import os
import io
from PIL import Image
from src.epub_io.opf import OPFData, ManifestItem, set_language_tree

def set_language(data: OPFData, language: str) -> OPFData:
    if not language or not language.strip():
        raise ValueError("Language code cannot be empty")

    set_language_tree(data, language.strip().lower())
    return data


def set_cover_from_path(epub_path: str, new_image_path: str, cover_item: ManifestItem) -> None:
    cover_zip_path = cover_item.href
    tmp_path = epub_path + ".tmp"

    with open(new_image_path, "rb") as img_f:
        new_image_bytes = img_f.read()

    set_cover(epub_path, tmp_path, cover_zip_path, new_image_bytes)


def set_cover_from_image(epub_path: str, img: Image.Image, cover_item: ManifestItem) -> None:
    cover_zip_path = cover_item.href
    tmp_path = epub_path + ".tmp"

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=100)
    new_image_bytes = buf.getvalue()

    set_cover(epub_path, tmp_path, cover_zip_path, new_image_bytes)


def set_cover(epub_path: str, tmp_path: str, cover_zip_path: str, new_image_bytes) -> None:
    with zipfile.ZipFile(epub_path, "r") as src, zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            if item.filename.endswith(cover_zip_path):
                dst.writestr(item, new_image_bytes)
            else:
                dst.writestr(item, src.read(item.filename))

    os.replace(tmp_path, epub_path)


def download_cover(epub_path: str, opf_path: str, cover_item: ManifestItem):
    cover_zip_path = cover_item.href

    opf_dir = os.path.dirname(opf_path)
    full_path = os.path.join(opf_dir, cover_zip_path) if opf_dir else cover_zip_path

    with zipfile.ZipFile(epub_path, "r") as epub:
        image_bytes = epub.read(full_path)

    output_name = os.path.basename(cover_zip_path)
    with open(output_name, "wb") as f:
        f.write(image_bytes)

    print(f"Saved cover to ./{output_name}")
