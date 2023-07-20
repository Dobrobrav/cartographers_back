# NOT FINISHED!!
# TODO: rename functions to be like the first func


from games.common import FieldRegular, ETerrainTypeAll


def count_the_outpost_points(field: FieldRegular) -> int:
    """
    Получите 2 ПО за каждую клетку во второй по величине области
    из клеток поселений
    (она может быть равна по величине самой большой такой области).
    """
    return 2 * count_area_cells(field, size_order=2)


def calc_the_promised_land(field: FieldRegular) -> int:
    """
    Получите 3 ПО за каждую область из клеток поселений, примыкающую
    к областям трёх или более разных типов местности.
    """
    return 3 * cals_areas_surrounded_by_other_areas(
        field,
        surrounding_area_types_count=3,
    )


def calc_the_great_city(field: FieldRegular) -> int:
    """
    Получите 1 ПО за каждую клетку в самой большой области
    из клеток поселений, не примыкающей ни к одной клетке гор.
    """
    return 1 * calc_area_cells_count(
        field,
        terrain_type=ETerrainTypeAll.VILLAGE,
    )


def calc_calderas(field: FieldRegular) -> int:
    """
    Получите 1 ПО за каждую незаполненную клетку, окружённую
    с четырёх сторон заполненными клетками или краями карты владений.
    """
    return 1 * calc_cells_surrounded_by_terrain_or_edge(field)


def calc_broken_roads(field: FieldRegular) -> int:
    """
    Получите 3 ПО за каждую диагональ,
    полностью состоящую из заполненных клеток
    и касающуюся левого и нижнего краёв карты владений.
    """
    return 3 * calc_filled_left_to_bottom_diagonals_count(field)


def calc_vast_plains(field: FieldRegular) -> int:
    """
    Получчите 6 ПО за каждый ряд или столбец,
    полностью состоящий из заполненных клеток.
    """
    return 6 * calc_filled_rows_or_columns_count(field)


def calc_mountain_grove(field: FieldRegular) -> int:
    """
    Получите 3 ПО за каждую клетку гор,
    соединённую с другой клеткой гор областью из клеток леса.
    """
    return 3 * calc_cells_connected_indirectly(
        cells_terrain_type=ETerrainTypeAll.MOUNTAIN,
        mediator_terrain_type=ETerrainTypeAll.FOREST
    )


def calc_sentinel_wood(field: FieldRegular) -> int:
    """
    Получите 1 ПО за каждую клетку леса,
    примыкающую к краю карты владений.
    """
    return 1 * calc_cells_touching_edge(
        field,
        terrain_type=ETerrainTypeAll.FOREST,
    )


def calc_enchanters_dell(field: FieldRegular) -> int:
    """
    1: Получите 2 ПО за каждую клетку водоёма, примыкающую к клетке гор.
    2: Получите 1 ПО за каждую клетку полей, примыкающую к клетке гор.
    """
    first = calc_cells_touching_other_cells(
        field,
        cells_type=ETerrainTypeAll.WATER,
        other_cells_type=ETerrainTypeAll.MOUNTAIN,
    )
    second = calc_cells_touching_other_cells(
        field,
        cells_type=ETerrainTypeAll.FIELD,
        other_cells_type=ETerrainTypeAll.MOUNTAIN,
    )
    return first + second


def calc_gold_vein(field: FieldRegular) -> int:
    """
    1: Получите 1 ПО за каждую клетку водоёма, примыкающую к клетке руин.
    2: Получите 3 ПО за каждую клетку полей, нарисованную на клетке руин.
    """
    # TODO: need to consider that ruins cell can be several types:
    # TODO: ruins-water, ruins-field and so on.
    first = calc_cells_touching_other_cells(
        field,
        cells_type=ETerrainTypeAll.WATER,
        other_cells_type=ETerrainTypeAll.RUINS,
    )
    second = calc_cells_drawn_on_ruins(
        field,
        cells_type=ETerrainTypeAll.FIELD,
    )
    return first + second


def calc_lakefolk_map(field: FieldRegular) -> int:
    """
    1: Получите 1 ПО за каждую клетку полей,
    примыкающую хотя бы к одной клетке водоёма.
    2: Получите 1 ПО за каждую клетку водоёма,
    примыкающую хотя бы к одной клетке полей.
    """
    first = calc_cells_touching_other_cells(
        field,
        cells_type=ETerrainTypeAll.FIELD,
        other_cells_type=ETerrainTypeAll.WATER,
        more_than_one_allowed=True,
    )
    second = calc_cells_touching_other_cells(
        field,
        cells_type=ETerrainTypeAll.WATER,
        other_cells_type=ETerrainTypeAll.FIELD,
    )
    return first + second


def calc_green_land(field: FieldRegular) -> int:
    """
    Получите 1 ПО за каждый ряд и каждый столбец,
    в которых есть хотя бы 1 клетка леса.
    Одна и та же клетка может быть учтена одновременно
    и для ряда, и для столбца.
    """
    return calc_rows_and_columns_with_cell(
        field,
        cell_type=ETerrainTypeAll.FOREST,
    )
