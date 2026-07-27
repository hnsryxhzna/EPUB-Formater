import re
import zipfile

from src.epub_io.container import get_opf_path
from src.epub_io.opf import parse_opf, save_opf
from src.operations.metadata import set_language


def _read_opf(epub_path):
    opf_path = get_opf_path(epub_path)
    with zipfile.ZipFile(epub_path) as z:
        return z.read(opf_path).decode("utf-8")


def _metadata_tags(opf_xml):
    block = re.search(r"<metadata.*?</metadata>", opf_xml, re.S)
    assert block, "no metadata block found"
    return sorted(re.findall(r"<(dc:\w+|meta)\b", block.group(0)))


def test_set_language_changes_language(make_epub):
    epub = make_epub()

    data = parse_opf(epub, get_opf_path(epub))
    set_language(data, "ja")
    save_opf(epub, get_opf_path(epub), data)

    reparsed = parse_opf(epub, get_opf_path(epub))
    assert reparsed.language == "ja"


def test_set_language_preserves_other_metadata(make_epub):
    epub = make_epub()

    before_tags = _metadata_tags(_read_opf(epub))

    data = parse_opf(epub, get_opf_path(epub))
    set_language(data, "ja")
    save_opf(epub, get_opf_path(epub), data)

    after_tags = _metadata_tags(_read_opf(epub))

    assert after_tags == before_tags
    after_opf = _read_opf(epub)
    for kept in ("Public Domain", "2020-01-01", "Test Press", "dcterms:modified"):
        assert kept in after_opf


def test_set_language_normalizes_and_manifest_survives(make_epub):
    epub = make_epub()

    data = parse_opf(epub, get_opf_path(epub))
    set_language(data, "  EN  ")
    save_opf(epub, get_opf_path(epub), data)

    reparsed = parse_opf(epub, get_opf_path(epub))
    assert reparsed.language == "en"
    assert len(reparsed.manifest) == 2
    assert len(reparsed.spine) == 1


def test_empty_language_rejected(make_epub):
    epub = make_epub()
    data = parse_opf(epub, get_opf_path(epub))

    import pytest
    with pytest.raises(ValueError):
        set_language(data, "   ")
