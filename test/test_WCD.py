from Geometry.WCD import WCD


def test_get_wcd():
    wcte = WCD('wcte', kind='WCTE')

    locations = []
    directions_x = []
    directions_z = []

    for mpmt in wcte.mpmts:
        location, direction_x, direction_z = mpmt.get_placement('design', wcte)
        locations.append(location)
        directions_x.append(direction_x)
        directions_z.append(direction_z)

    assert wcte is not None


def test_wcd():
    assert False
