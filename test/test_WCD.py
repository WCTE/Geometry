from Geometry.WCD import WCD


def test_get_wcd():
    wcte = WCD('wcte', kind='WCTE')

    locations = []
    directions_x = []
    directions_z = []

    for mpmt in wcte.mpmts:
        p = mpmt.get_placement('design', wcte)
        locations.append(p['location'])
        directions_x.append(p['direction_x'])
        directions_z.append(p['direction_z'])

    assert wcte is not None


def test_wcd():
    assert False
