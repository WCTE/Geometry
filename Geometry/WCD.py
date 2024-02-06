"""
WCD: A water Cherenkov detector consisting of a set of MPMTs or a set of Super Modules

properties:
    - mpmts: an array of MPMTs (defined if the WCD is made of MPMTs or Super Modules)
    - sms: an array of Super Modules (defined if the WCD is made of Super Modules)

The WCTE is constructed from 3 Super Modules (bottom, barrel, top) and has a cartesian coordinate system with its origin
at the location where the beam intersects the cylinder axis. The beam follows the "z" direction and "y" direction
is pointing up.
"""

import numpy as np

from Geometry.Device import Device
from Geometry.MPMT import MPMT
from Geometry.SM import SM


class WCD(Device):
    """A water cherenkov detector"""

    # class properties:
    light_velocity = 2.99792E2  # speed of light in vacuum (mm/ns)

    prop_mean = {}  # dictionary of mean properties of different kinds of WCDs
    prop_scale = {}  # scale of variations of properties used to create objects
    prop_var = {}  # distribution of variations

    # A dictionary of mpmt kinds and placements in the WCD:
    mpmts_design = {}

    # A dictionary of calib_source kinds and placements in the WCD:
    calibs_design = {}

    # default properties of WCDs
    # all properties are defined by primitives, so shallow dictionary copy works
    # if new properties are needed, be sure to add to def_prop_mean
    # and def_prop_scale
    def_prop_mean = {'clock_offset': 0.,  # ns offset to reference clock
                     'refraction_index': 1.4,
                     'absorption_length': 80.E3  # 80 m
                     }
    def_prop_scale = {'clock_offset': 0.,
                      'refraction_index': 0.,
                      'absorption_length': 1.E3
                      }
    def_prop_var = {}

    def_calibs = []
    # one calibration beacon located somewhere
    def_calibs.append({'kind': 'L1',
                       'loc': [1000., 1500., 2000., ],
                       'loc_sig': [0.0, 0.0, 0.0],
                       'rot_axes': 'XZ',
                       'rot_angles': [0., 0.],
                       'rot_angles_sig': [0.0, 0.]})

    def_mpmts = []
    # two pairs of mPMTs facing each other:
    for i in range(2):
        for j in range(2):
            sign_x = 2 * i - 1
            x_mpmt = sign_x * 4000.
            z_mpmt = (2 * j - 1) * 1000.
            def_mpmts.append({'kind': 'M1',
                              'loc': [x_mpmt, 0., z_mpmt],
                              'loc_sig': [1.0, 1.0, 1.0],
                              'rot_axes': 'XYZ',
                              'rot_angles': [np.pi / 2., -1. * sign_x * np.pi / 2., 0.],
                              'rot_angles_sig': [0.01, 0.01, 0.01]})

    def3_mpmts = def_mpmts.copy()
    # 3 pairs of mPMTs
    def3_mpmts.append({'kind': 'M1',
                       'loc': [0., 0., -4000.],
                       'loc_sig': [1.0, 1.0, 1.0],
                       'rot_axes': 'XYZ',
                       'rot_angles': [0., 0., 0.],
                       'rot_angles_sig': [0.01, 0.01, 0.01]})
    def3_mpmts.append({'kind': 'M1',
                       'loc': [0., 0., 4000.],
                       'loc_sig': [1.0, 1.0, 1.0],
                       'rot_axes': 'XYZ',
                       'rot_angles': [np.pi, 0., 0.],
                       'rot_angles_sig': [0.01, 0.01, 0.01]})
    def3_mpmts.append({'kind': 'M1',
                       'loc': [0., -4000., 0.],
                       'loc_sig': [1.0, 1.0, 1.0],
                       'rot_axes': 'XYZ',
                       'rot_angles': [-np.pi / 2., 0., 0.],
                       'rot_angles_sig': [0.01, 0.01, 0.01]})
    def3_mpmts.append({'kind': 'M1',
                       'loc': [0., 4000., 0.],
                       'loc_sig': [1.0, 1.0, 1.0],
                       'rot_axes': 'XYZ',
                       'rot_angles': [np.pi / 2., 0., 0.],
                       'rot_angles_sig': [0.01, 0.01, 0.01]})

    # Standard WCD:
    w1_prop_mean = def_prop_mean.copy()
    w1_prop_scale = def_prop_scale.copy()
    w1_prop_var = def_prop_var.copy()

    prop_mean['W1'] = w1_prop_mean
    prop_scale['W1'] = w1_prop_scale
    prop_var['W1'] = w1_prop_var

    mpmts_design['W1'] = def_mpmts
    calibs_design['W1'] = def_calibs

    # 6 mPMT Standard WCD:
    w3_prop_mean = def_prop_mean.copy()
    w3_prop_scale = def_prop_scale.copy()
    w3_prop_var = def_prop_var.copy()

    prop_mean['W3'] = w3_prop_mean
    prop_scale['W3'] = w3_prop_scale
    prop_var['W3'] = w3_prop_var

    mpmts_design['W3'] = def3_mpmts
    calibs_design['W3'] = def_calibs

    # Standard WCD in air:
    w2_prop_mean = def_prop_mean.copy()
    w2_prop_mean['refraction_index'] = 1.0
    w2_prop_mean['absorption_length'] = 80.E6
    w2_prop_scale = def_prop_scale.copy()
    w2_prop_var = def_prop_var.copy()

    prop_mean['W2'] = w2_prop_mean
    prop_scale['W2'] = w2_prop_scale
    prop_var['W2'] = w2_prop_var

    mpmts_design['W2'] = def_mpmts
    calibs_design['W2'] = def_calibs

    # Super module based designs:
    sms_design = {}

    # WCTE
    ######

    wcte_prop_mean = def_prop_mean.copy()
    wcte_prop_scale = def_prop_scale.copy()
    wcte_prop_var = def_prop_var.copy()

    prop_mean['WCTE'] = wcte_prop_mean
    prop_scale['WCTE'] = wcte_prop_scale
    prop_var['WCTE'] = wcte_prop_var

    # The WCTE has 4 rows of barrel mPMTs, with the beam window on the second row from bottom
    # Use the centre of the beam window as the height, y = 0
    # Separation of top and bottom = 3060.475 mm
    # wcte_bottom: -1 * (half of mPMT baseplate width + barrel_vertical_pitch + 261.475 mm) = -(528/2. + 580 + 261.475)
    # wcte_top: half of mPMT baseplate width + 2*barrel_vertical_pitch + 531 mm = 528/2. + 2*580 + 531 = 1955 mm

    wcte_top = 1955.  # mm y coordinate of mPMT base plates on top endcap
    wcte_bottom = -1105.475  # mm y coordinate of mPMT base plates on bottom endcap

    loc_sig = [1.0, 1.0, 1.0]  # mm positioning accuracy
    rot_angles_sig = [0.01, 0.01, 0.01]  # rad rotational angle positioning accuracy

    wcte_sms = []

    wcte_sms.append({'name': 'bottom', 'kind': 'bottom',
                     'loc': [0., wcte_bottom, 0.],
                     'loc_sig': loc_sig,
                     'rot_axes': 'ZYX',
                     'rot_angles': [-np.pi / 2., -np.pi / 2., 0.],
                     'rot_angles_sig': rot_angles_sig})

    wcte_sms.append({'name': 'barrel', 'kind': 'barrel',
                     'loc': [0., 0., 0.],
                     'loc_sig': loc_sig,
                     'rot_axes': 'ZYX',
                     'rot_angles': [-np.pi / 2., -np.pi / 2., 0.],
                     'rot_angles_sig': rot_angles_sig})

    wcte_sms.append({'name': 'top', 'kind': 'top',
                     'loc': [0., wcte_top, 0.],
                     'loc_sig': loc_sig,
                     'rot_axes': 'ZYX',
                     'rot_angles': [-np.pi / 2., -np.pi / 2., 0.],
                     'rot_angles_sig': rot_angles_sig})

    sms_design['WCTE'] = wcte_sms

    def __init__(self, name, container=None, kind='WCTE', place_design={}, place_true={}, device_type=SM):
        super().__init__(WCD, name, container, kind, place_design, place_true)

        # create and place the set of devices
        if device_type == MPMT:
            self.mpmts = self.place_devices(device_type, self.mpmts_design, kind)
            self.sms = None
            self.cameras = None
        elif device_type == SM:
            self.sms = self.place_devices(device_type, self.sms_design, kind)
            # collect all the mpmts in the WCD
            self.mpmts = []
            for sm in self.sms:
                sm.get_mpmts(self.mpmts)
            # give each mpmt a unique name
            for i, mpmt in enumerate(self.mpmts):
                mpmt.name = str(i)
            # collect all the cameras in the WCD
            self.cameras = []
            for sm in self.sms:
                sm.get_cameras(self.cameras)
            # give each camera a unique name
            for i, camera in enumerate(self.cameras):
                camera.name = str(i)
