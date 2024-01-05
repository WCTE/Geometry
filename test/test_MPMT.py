from Geometry.MPMT import MPMT


def test_get_mpmt():
    test_mpmt = MPMT('test_mpmt', kind='ME')
    print()
    pmt1 = test_mpmt.pmts[1]
    location, direction_x, direction_z = pmt1.get_placement('design', test_mpmt)
    print(location, direction_x, direction_z)
    location2, direction_x2, direction_z2 = pmt1.get_placement('design')

    assert test_mpmt is not None


def test_mpmt():
    test_mpmt = MPMT('test_mpmt', kind='ME')
    locations = []
    directions_x = []
    directions_z = []

    for pmt in test_mpmt.pmts:
        location, direction_x, direction_z = pmt.get_placement('design', test_mpmt)
        locations.append(location)
        directions_x.append(direction_x)
        directions_z.append(direction_z)

    assert test_mpmt is not None


def test_get_xy_points():
    assert False
