from Geometry.HALL import HALL

def test_hall():
    t9_area = HALL('wcte', kind='WCTE')

    assert t9_area is not None
