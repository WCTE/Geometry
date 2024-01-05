from Geometry.PMT import PMT


def test_get_pmt():
    my_pmt = PMT('my_pmt', kind='P3')
    for key in my_pmt.get_properties('design'):
        print(key, my_pmt.get_properties('design')[key], PMT.design_desc[key])

    print(my_pmt.get_properties('true'))
    PMT.design_mean['P3']['delay'] = 100.
    PMT.design_scale['P3']['delay'] = 10.
    my_pmt2 = PMT('my_pmt2')
    print('pmt:', my_pmt.get_properties('design')['delay'], my_pmt.get_properties('true')['delay'])
    print('pmt2:', my_pmt2.get_properties('design')['delay'],my_pmt2.get_properties('true')['delay'])

    my_pmt.set_property('delay', 200.)
    print('pmt:', my_pmt.get_properties('design')['delay'], my_pmt.get_properties('true')['delay'])

    assert my_pmt is not None


def test_get_xy_points():
    assert False
