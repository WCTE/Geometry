from Geometry.CAMERA import CAMERA


def test_get_camera():
    my_camera = CAMERA('my_camera')
    for key in my_camera.get_properties('design'):
        print(key, my_camera.get_properties('design')[key], CAMERA.design_desc[key])

    print(my_camera.get_properties('true'))

    assert my_camera is not None