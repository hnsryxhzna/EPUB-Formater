import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from .container import get_opf_path
import sys
import shutil
import os

OPF_NS  = "http://www.idpf.org/2007/opf"
DC_NS   = "http://purl.org/dc/elements/1.1/"

NS = {
    "opf": OPF_NS,
    "dc":  DC_NS,
}


@dataclass
class ManifestItem:
    id:         str
    href:       str
    media_type: str
    properties: str = ""


@dataclass
class SpineItem:
    idref:  str
    linear: bool = True


@dataclass
class OPFData:
    title:          str = ""
    author:         str = ""
    language:       str = ""
    publisher:      str = ""
    identifier:     str = ""
    cover_meta_id:  str = ""

    manifest: list[ManifestItem] = field(default_factory=list)
    spine:    list[SpineItem]    = field(default_factory=list)
    tree: ET.ElementTree | None  = field(default=None, repr=False, compare=False)


def parse_opf(epub_path: str, opf_path: str) -> OPFData:
    with zipfile.ZipFile(epub_path, "r") as epub:
        with epub.open(opf_path) as f:
            tree = ET.parse(f)

    root = tree.getroot()
    data = OPFData()
    data.tree = tree

    _parse_metadata(root, data)
    _parse_manifest(root, data)
    _parse_spine(root, data)

    return data


def save_opf(epub_path: str, opf_path: str, data: OPFData) -> None:
    if data.tree is None:
        raise ValueError("Cannot save")

    ET.register_namespace("", OPF_NS)
    ET.register_namespace("dc", DC_NS)
    opf_bytes = ET.tostring(
        data.tree.getroot(), encoding="utf-8", xml_declaration=True
    )

    tmp_path = epub_path + ".tmp"

    with zipfile.ZipFile(epub_path, "r") as src, \
         zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as dst:

        for item in src.infolist():
            if item.filename == opf_path:
                dst.writestr(item, opf_bytes)
            else:
                dst.writestr(item, src.read(item.filename))

    os.replace(tmp_path, epub_path)


def get_cover_item(data: OPFData) -> ManifestItem | None:
    for item in data.manifest:
        if "cover-image" in item.properties:
            return item

    cover_id = data.cover_meta_id
    if cover_id:
        for item in data.manifest:
            if item.id == cover_id:
                return item

    return None


def _parse_metadata(root: ET.Element, data: OPFData) -> None:
    meta = root.find("opf:metadata", NS)
    if meta is None:
        return

    def text(tag: str) -> str:
        element = meta.find(tag, NS)
        return element.text.strip() if element is not None and element.text else ""

    data.title = text("dc:title")
    data.author = text("dc:creator")
    data.language = text("dc:language")
    data.publisher = text("dc:publisher")
    data.identifier = text("dc:identifier")
    for cover in meta.findall("opf:meta", NS):
        if cover.get("name") == "cover":
            data.cover_meta_id = cover.get("content", "")


def _parse_manifest(root: ET.Element, data: OPFData) -> None:
    manifest = root.find("opf:manifest", NS)
    if manifest is None:
        return

    for item in manifest.findall("opf:item", NS):
        data.manifest.append(ManifestItem(
            id = item.get("id", ""),
            href = item.get("href", ""),
            media_type = item.get("media-type", ""),
            properties = item.get("properties", ""),
        ))


def _parse_spine(root: ET.Element, data: OPFData) -> None:
    spine = root.find("opf:spine", NS)
    if spine is None:
        return

    for itemref in spine.findall("opf:itemref", NS):
        linear_attr = itemref.get("linear", "yes")
        data.spine.append(SpineItem(
            idref  = itemref.get("idref", ""),
            linear = linear_attr.lower() != "no",
        ))


def set_language_tree(data: OPFData, language: str) -> None:
    if data.tree is None:
        raise ValueError("No parsed OPF tree to edit")

    root = data.tree.getroot()
    meta = root.find("opf:metadata", NS)
    if meta is None:
        raise ValueError("No metadata element in OPF")

    lang = meta.find("dc:language", NS)
    if lang is None:
        lang = ET.SubElement(meta, f"{{{DC_NS}}}language")
    lang.text = language

    data.language = language


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: opf.py <path_to_your_file.epub>", file = sys.stderr)
        sys.exit(2)

    opf_path = get_opf_path(sys.argv[1])
    data = parse_opf(sys.argv[1], opf_path)
    print(data.language)
