from Geometry.WCD import WCD
import json


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


def test_wcd_json():
    wcte = WCD('wcte', kind='WCTE')

    wcte.save_json('wcte_design.json', 'design', 'design', devices='all')

    assert wcte is not None

def test_wcd_json_load():
    info = json.load(open('wcte_design.json'))

    p = info['mpmts']['43']['leds']['3']['placement']

    assert info is not None
