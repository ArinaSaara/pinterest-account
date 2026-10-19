"""PDF post-processing shared by the planner and sticker-pack builders."""
import io
import sys
import threading

from PIL import Image
from pypdf import PdfWriter
from pypdf.generic import NameObject


def _lighten(path, quality):
    sys.setrecursionlimit(100000)  # long outlines are deep linked lists
    w = PdfWriter(clone_from=path); seen = set()
    for page in w.pages:
        xo = page["/Resources"].get("/XObject")
        for ref in (xo.get_object().values() if xo else []):
            o = ref.get_object()
            if ref.idnum in seen or o.get("/Subtype") != "/Image" or "/SMask" not in o:
                continue
            seen.add(ref.idnum)
            im = Image.frombytes("RGB", (o["/Width"], o["/Height"]), o.get_data())
            buf = io.BytesIO(); im.save(buf, "JPEG", quality=quality, optimize=True)
            o._data = buf.getvalue(); o[NameObject("/Filter")] = NameObject("/DCTDecode"); o.pop("/DecodeParms", None)
    w.write(path)


def lighten(path, quality=90):
    """reportlab stores image pixels as raw flate; re-encode the colour layer as JPEG (alpha mask kept), ~4x smaller."""
    threading.stack_size(512 * 1024 * 1024)
    t = threading.Thread(target=_lighten, args=(path, quality)); t.start(); t.join()
