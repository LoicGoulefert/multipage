from copy import deepcopy
from typing import Tuple
import click
import vpype as vp
from vpype.geometry import crop
import numpy as np
from vpype.model import LineCollection


def _to_portrait(document: vp.Document, size: Tuple[float, float]) -> vp.Document:
    reoriented_doc = vp.Document(page_size=(size[1], size[0]))
    document.translate(-size[0] / 2, -size[1] / 2)
    document.rotate(np.pi / 2)
    document.translate(size[1] / 2, size[0] / 2)

    for layer, lc in document.layers.items():
        reoriented_doc.add(lc, layer)

    return reoriented_doc


def _get_half_crops(
    lc: vp.LineCollection, size: Tuple[float, float]
) -> Tuple[LineCollection, LineCollection]:
    upper_half_lc = deepcopy(lc)
    lower_half_lc = deepcopy(lc)
    upper_half_lc.crop(0, size[1] / 2, size[0], 0)
    lower_half_lc.crop(0, size[1], size[0], size[1] / 2)

    return upper_half_lc, lower_half_lc


@click.command()
@click.option("-o", "--overlap", type=vp.LengthType(), default=0)
@vp.global_processor
def multipage(document: vp.Document, overlap: vp.LengthType) -> vp.Document:
    """
    ...
    """
    size = document.page_size
    print("Input size =", size)

    # Convert to portrait
    if size[0] > size[1]:
        document = _to_portrait(document, size)
        size = document.page_size

    # Now size[0] < size[1]
    print("New size =", size)

    # new_doc = vp.Document(page_size=(size[0], size[1] / 2))
    new_doc = vp.Document(page_size=size)

    for layer, lc in document.layers.items():
        upper_half_lc, lower_half_lc = _get_half_crops(lc, size)
        new_doc.add(upper_half_lc, layer)
        new_doc.add(lower_half_lc, layer + 1)

    print("new_doc size=", new_doc.page_size)
    return new_doc


multipage.help_group = "Plugins"
