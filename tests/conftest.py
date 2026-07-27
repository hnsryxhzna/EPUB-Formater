import io
import zipfile
import pytest
from PIL import Image

CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

DEFAULT_OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="pub-id">urn:uuid:12345</dc:identifier>
    <dc:title>Test Book</dc:title>
    <dc:creator>Ada Lovelace</dc:creator>
    <dc:language>en</dc:language>
    <dc:date>2020-01-01</dc:date>
    <dc:publisher>Test Press</dc:publisher>
    <dc:rights>Public Domain</dc:rights>
    <dc:subject>Fiction</dc:subject>
    <meta property="dcterms:modified">2020-01-01T00:00:00Z</meta>
    <meta name="cover" content="cover-image"/>
  </metadata>
  <manifest>
    <item id="cover-image" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>
    <item id="content" href="content.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="content"/>
  </spine>
</package>
"""

CONTENT_XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><body><p>Hello.</p></body></html>
"""


def _make_cover_bytes(size=(80, 120), fmt="JPEG"):
    buf = io.BytesIO()
    Image.new("RGB", size, (120, 90, 200)).save(buf, format=fmt)
    return buf.getvalue()


@pytest.fixture
def make_epub(tmp_path):
    counter = {"n": 0}

    def _factory(opf=DEFAULT_OPF, cover_size=(80, 120), cover_fmt="JPEG"):
        counter["n"] += 1
        path = tmp_path / f"book{counter['n']}.epub"

        with zipfile.ZipFile(path, "w") as z:
            z.writestr("mimetype", "application/epub+zip",
                       compress_type=zipfile.ZIP_STORED)
            z.writestr("META-INF/container.xml", CONTAINER_XML)
            z.writestr("OEBPS/content.opf", opf)
            z.writestr("OEBPS/content.xhtml", CONTENT_XHTML)
            z.writestr("OEBPS/cover.jpg",
                       _make_cover_bytes(cover_size, cover_fmt))

        return str(path)

    return _factory
