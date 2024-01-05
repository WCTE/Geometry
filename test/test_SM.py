from Geometry.SM import SM
import numpy as np


def test_get_sm():
    my_sm = SM('my_sm', kind='SSM')

    pmt0 = my_sm.mpmts[0].pmts[0]
    pd = pmt0.get_placement('design')
    pdm = pmt0.get_placement('design', my_sm.mpmts[0])

    assert my_sm is not None


class TestSM(SM):
    # define new supermodules: SSM2 and SMSM
    # SSM2 is a 2x2 rectangular pattern of 'MR' MPMTs
    # SMSM is two 'SSM2's at 90 degrees to each other

    def_mpmts2 = []
    # 2 x 2 rectangular pattern of MPMTs (for testing):
    for i in range(-1, 1):
        for j in range(-1, 1):
            def_mpmts2.append({'name': str(len(def_mpmts2)), 'kind': 'MR',
                               'loc': [800. * (i + 0.5), 800. * (j + 0.5), -150., ],
                               'loc_sig': [1.0, 1.0, 1.0],
                               'rot_axes': 'XZ',
                               'rot_angles': [0., 0.],
                               'rot_angles_sig': [0.01, 0.01]})

    SM.devices_design['SSM2'] = def_mpmts2

    def_sms = []
    # two super modules at 90 degrees to each other
    def_sms.append({'name': '0', 'kind': 'SSM2',
                    'loc': [1000., 0., 1000.],
                    'loc_sig': [1.0, 1.0, 1.0],
                    'rot_axes': 'Y',
                    'rot_angles': [-np.pi / 2.],
                    'rot_angles_sig': [0.02]})
    def_sms.append({'name': '1', 'kind': 'SSM2',
                    'loc': [0., 1000., 1000.],
                    'loc_sig': [1.0, 1.0, 1.0],
                    'rot_axes': 'ZY',
                    'rot_angles': [np.pi / 2., -np.pi / 2.],
                    'rot_angles_sig': [0.01, 0.01]})
    SM.devices_design['SMSM'] = def_sms


def test_get_sm2():
    my_sm2 = TestSM('my_sm2', kind='SSM2')

    pmt0 = my_sm2.mpmts[0].pmts[0]
    pd = pmt0.get_placement('design')
    pdm = pmt0.get_placement('design', my_sm2.mpmts[0])

    assert my_sm2 is not None


def test_get_smsm():
    my_smsm = TestSM('my_smsm', kind='SMSM', device_type=SM)

    print('comparing locations and directions of pmts in SMSM')
    for ism in range(2):
        for coord in [my_smsm.sms[ism].mpmts[0], my_smsm.sms[ism], my_smsm]:
            for ipmt in range(2):
                pmt = my_smsm.sms[ism].mpmts[0].pmts[ipmt]
                p = pmt.get_placement('design', coord)
                print(ism, ipmt, p)

    assert my_smsm is not None


def test_get_wall():
    my_wall = SM('wall', kind='wall')
    mpmt_list = []
    my_wall.get_mpmts(mpmt_list)

    locations = []
    directions_x = []
    directions_z = []

    for mpmt in my_wall.mpmts:
        p = mpmt.get_placement('design', my_wall)
        locations.append(p['location'])
        directions_x.append(p['direction_x'])
        directions_z.append(p['direction_z'])

    assert my_wall is not None
