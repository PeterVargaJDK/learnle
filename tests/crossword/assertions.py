from learnle_site.utils.crossword_grid import UnpackedCrosswordGrid
from learnle_site.datatypes import Dimensions


def assert_grid_equals(grid: UnpackedCrosswordGrid, expected_grid_text_view: str):
    actual_clean_text_view = grid.text_view()
    print('\n' + actual_clean_text_view)
    lines = []
    for line in expected_grid_text_view.strip().splitlines():
        lines.append(line.strip())
    assert actual_clean_text_view == '\n'.join(lines)
    assert grid.dimensions == Dimensions(len(lines[0]), len(lines))
