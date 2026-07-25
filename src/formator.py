from PIL import Image
from .epub_io.container import get_opf_path
from .epub_io.opf import parse_opf, save_opf, get_cover_item
from .operations.metadata import set_language, set_cover_from_path, set_cover_from_image, download_cover
from .operations.cover_info import cover_info_epub
from .operations.cover_resize import resize_cover

class EpubFormator:
    def __init__(self, epub_path: str):
        self.epub_path  = epub_path
        self.opf_path   = get_opf_path(epub_path)
        self.data       = parse_opf(epub_path, self.opf_path)
        self.cover_item = get_cover_item(self.data)
        self.has_cover  = not (self.cover_item is None)


    def get_title(self):
        return self.data.title
    

    def get_author(self):
        return self.data.author


    def get_language(self):
        return self.data.language


    def get_cover(self):
        return self.data.cover_meta_id
    

    def get_epub_info(self):
        print(f"Title:    {self.get_title()}")
        print(f"Author:   {self.get_author()}")
        print(f"Language: {self.get_language()}")
        print(f"Cover ID: {self.get_cover()}")


    def set_language(self, language: str) -> None:
        set_language(self.data, language)
        save_opf(self.epub_path, self.opf_path, self.data)
        print(f"Language set to '{language}'")


    def set_cover(self, cover: str) -> None:
        if self.cover_item is None:
            raise ValueError("No cover image found in this EPUB")
        set_cover_from_path(self.epub_path, cover, self.cover_item)
        save_opf(self.epub_path, self.opf_path, self.data)
        print(f"Cover replaced with '{cover}'")


    def resize_cover(self, method: str, ratio: float) -> None:
        new_cover = resize_cover(self.epub_path, self.opf_path, self.cover_item, method, ratio)
        self.download_cover()
        set_cover_from_image(self.epub_path, new_cover, self.cover_item)
        print(f"Cover resized using '{method}' with ratio {ratio}")


    def download_cover(self) -> None:
        download_cover(self.epub_path, self.opf_path, self.cover_item)


    def cover_info(self) -> None:
        cover_info_epub(self.epub_path, self.opf_path, self.cover_item)
