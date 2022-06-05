from copy import deepcopy
from typing import Tuple

import click
import numpy as np
import vpype as vp
import vpype_cli
from shapely.geometry import LineString, Polygon
from shapely.strtree import STRtree


def _to_portrait(document: vp.Document, size: Tuple[float, float]) -> vp.Document:
    reoriented_doc = vp.Document(page_size=(size[1], size[0]))
    document.translate(-size[0] / 2, -size[1] / 2)
    document.rotate(np.pi / 2)
    document.translate(size[1] / 2, size[0] / 2)

    for layer, lc in document.layers.items():
        reoriented_doc.add(lc, layer)

    return reoriented_doc


def _get_query_geoms(size: float, overlap: float) -> Tuple[LineString, LineString, LineString]:
    half_h = size[1] / 2
    offset = overlap / 2
    upper_rect = LineString([(0, 0), (size[0], 0), (size[0], half_h), (0, half_h), (0, 0)])
    lower_rect = LineString(
        [(0, half_h), (size[0], half_h), (size[0], size[1]), (0, size[1]), (0, half_h)]
    )
    overlap_rect = LineString(
        [
            (0, half_h - offset),
            (size[0], half_h - offset),
            (size[0], half_h + offset),
            (0, half_h + offset),
            (0, half_h - offset),
        ]
    )

    return upper_rect, lower_rect, overlap_rect


def _get_half_crops(
    lc: vp.LineCollection, size: Tuple[float, float]
) -> Tuple[vp.LineCollection, vp.LineCollection]:
    upper_half_lc = deepcopy(lc)
    lower_half_lc = deepcopy(lc)
    upper_half_lc.crop(0, size[1] / 2, size[0], 0)
    lower_half_lc.crop(0, size[1], size[0], size[1] / 2)

    return upper_half_lc, lower_half_lc


@click.command()
@click.option("-o", "--overlap", type=vpype_cli.LengthType(), default=0, help="")
@click.option("-v", "--verbose", is_flag=True, default=False, help="print logs")
@vpype_cli.global_processor
def multipage(
    document: vp.Document, overlap: vpype_cli.LengthType, verbose: bool
) -> vp.Document:
    """
    ...
    """
    input_size = document.page_size
    layer_count = len(document.layers.keys())

    # Convert to portrait
    if input_size[0] > input_size[1]:
        document = _to_portrait(document, input_size)

    size = document.page_size
    new_doc = vp.Document(page_size=(size[0], size[1] / 2))
    upper_rect, lower_rect, overlap_rect = _get_query_geoms(size, overlap)

    for layer, lc in document.layers.items():
        print(f"Overlap={overlap}")
        line_array = []
        if overlap == 0:
            upper_half_lc, lower_half_lc = _get_half_crops(lc, size)
            lower_half_lc.translate(0, -size[1] / 2)
            lower_half_lc.rotate(np.pi)
            lower_half_lc.translate(size[0], size[1] / 2)
            new_doc.add(upper_half_lc, layer)
            new_doc.add(lower_half_lc, layer + layer_count)
        else:
            tree = STRtree(lc.as_mls().geoms)
            #  On va découper les geoms de ce layer à un point random DANS overlap_rect
            # plusieurs cas:
            # (1) geom 'within' overlap_rect -> pas de split
            # (2) geom 'intersect' overlap_rect -> ..?
            p = Polygon(overlap_rect)
            print(tree.query(p))

    if verbose:
        print()
        print("===== multipage =====")
        print(f"Input size: {input_size[0]:.2f} x {input_size[1]:.2f}")
        print(f"Output size: {new_doc.page_size[0]:.2f} x {new_doc.page_size[1]:.2f}")
        print("Layer correspondance table:")
        print("\n".join(f"{l+1} -> [{l+1}, {l+1+layer_count}]" for l in range(layer_count)))
        print()

    return new_doc


multipage.help_group = "Plugins"
