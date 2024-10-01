from weather_cases.environment.contours import get_contour_calc


def test_should_get_contours(sample_height_ds):
    contour_gen = get_contour_calc(include=12, delta=3)
    contours = contour_gen(sample_height_ds.Z)
    assert list(contours) == [6, 9, 12, 15, 18, 21]


def test_get_contours_min_above_include(sample_height_ds):
    contour_gen = get_contour_calc(include=2, delta=3)
    contours = contour_gen(sample_height_ds.Z)
    assert list(contours) == [8, 11, 14, 17, 20]


def test_get_contours_max_above_include(sample_height_ds):
    contour_gen = get_contour_calc(include=22, delta=3)
    contours = contour_gen(sample_height_ds.Z)
    assert list(contours) == [7, 10, 13, 16, 19, 22]
