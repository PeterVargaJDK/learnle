from learnle_site.domain.crosswords.crosswords_grid import (
    UnpackedCrosswordsGrid,
)
from learnle_site.utils import Dimensions


def assert_grid_equals(grid: UnpackedCrosswordsGrid, expected_grid_text_view: str):
    actual_clean_text_view = grid.text_view()
    print('\n' + actual_clean_text_view)
    lines = []
    for line in expected_grid_text_view.strip().splitlines():
        lines.append(line.strip())
    assert actual_clean_text_view == '\n'.join(lines)
    assert grid.dimensions == Dimensions(len(lines[0]), len(lines))
