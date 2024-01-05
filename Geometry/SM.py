from Geometry.Device import Device
from Geometry.MPMT import MPMT

import numpy as np
from scipy.spatial.transform import Rotation


class SM(Device):
    """A super module consists of a set of either mPMTs or super modules.
    It only has geometry information, no other properties.
    """

    # A dictionary of device kinds and placements in the super module:
    devices_design = {}

    ssm_mpmts = []
    # 3 x 2 rectangular pattern of MPMTs (for testing):
    for i in range(-1, 2):
        for j in range(-1, 1):
            ssm_mpmts.append({'name': str(len(ssm_mpmts)), 'kind': 'MR',
                              'loc': [600. * i, 600. * (j + 0.5), -100., ],
                              'loc_sig': [1.0, 1.0, 1.0],
                              'rot_axes': 'XZ',
                              'rot_angles': [0., 0.],
                              'rot_angles_sig': [0.01, 0.01]})

    devices_design['SSM'] = ssm_mpmts

    # Super modules that make up the WCTE WCD:
    # The z-axis for each super module is pointing upwards during each super module construction and their initial
    # surveys. Once assembled the WCTE z-axis is aligned with the beam direction

    tb_pitch = 580.  # mm separation of mPMT centres on top and bottom (x and y the same)
    wcte_diameter = 3422.166  # mm separation of mPMT baseplates on opposite wall locations
    wall_vertical_pitch = 580.  # mm separation of mPMT centres for rows

    loc_sig = [1.0, 1.0, 1.0]  # mm positioning accuracy
    rot_angle_sig = 0.01  # radians

    # Bottom super module:
    ######################
    # Origin and z-axis coincides with that of centre mPMT origin.
    # Ordering of MPTs increases with phi. Second mPMT is displaced along SM +x axis.

    bottom_mpmts = []

    # Start with mPMT at centre of bottom
    offsets = [[0., 0., 0.]]

    offs = [-tb_pitch, 0, tb_pitch]
    for i in range(8):
        offset = [offs[[2, 2, 1, 0, 0, 0, 1, 2][i]], offs[[1, 2, 2, 2, 1, 0, 0, 0][i]], 0.]
        offsets.append(offset)

    offs = [-2. * tb_pitch, -tb_pitch, 0, tb_pitch, 2. * tb_pitch]
    for i in range(12):
        offset = [offs[[4, 4, 3, 2, 1, 0, 0, 0, 1, 2, 3, 4][i]], offs[[2, 3, 4, 4, 4, 3, 2, 1, 0, 0, 0, 1][i]], 0.]
        offsets.append(offset)

    # rotate mPMTs to put feed-throughs in correct orientations... pi multiplier starting at #0
    y_rots = [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]

    for offset, y_rot in zip(offsets, y_rots):
        location = offset
        bottom_mpmts.append({
            'kind': 'ME',
            'loc': location,
            'loc_sig': loc_sig,
            'rot_axes': 'z',
            'rot_angles': (y_rot+0.5) * np.pi,
            'rot_angles_sig': rot_angle_sig
        })

    devices_design['bottom'] = bottom_mpmts

    # Top super module:
    ###################
    # Origin and z-axis coincides with that of centre mPMT origin.
    # Ordering of MPTs DECREASES with phi (as it will be flipped compared to bottom).
    # Second mPMT is displaced along SM +x axis.

    top_mpmts = []

    # Start with mPMT at centre of top SM
    offsets = [[0., 0., 0.]]

    offs = [-tb_pitch, 0, tb_pitch]
    for i in range(8):
        offset = [offs[[2, 2, 1, 0, 0, 0, 1, 2][i]], offs[[1, 0, 0, 0, 1, 2, 2, 2][i]], 0.]
        offsets.append(offset)

    offs = [-2. * tb_pitch, -tb_pitch, 0, tb_pitch, 2. * tb_pitch]
    for i in range(12):
        offset = [offs[[4, 4, 3, 2, 1, 0, 0, 0, 1, 2, 3, 4][i]], offs[[2, 1, 0, 0, 0, 1, 2, 3, 4, 4, 4, 3][i]], 0.]
        offsets.append(offset)

    # rotate mPMTs to put feed-throughs in correct orientations... pi multiplier
    #y_rots = [0, 1, 1, 1.5, 1.5, 0, 0, 0.5, 0.5, 1, 1, 1, 1.5, 1.5, 1.5, 0, 0, 0, 0.5, 0.5, 0.5]
    y_rots = [0, 1, 1, 0.5, 0.5, 0, 0, 1.5, 1.5, 1, 1, 1, 0.5, 0.5, 0.5, 0, 0, 0, 1.5, 1.5, 1.5]

    for offset, y_rot in zip(offsets, y_rots):
        location = offset
        top_mpmts.append({
            'kind': 'ME',
            'loc': location,
            'loc_sig': loc_sig,
            'rot_axes': 'z',
            'rot_angles': (y_rot-0.5) * np.pi,
            'rot_angles_sig': rot_angle_sig
        })

    devices_design['top'] = top_mpmts

    # Wall super module:
    ####################
    # Origin on cylinder axis, z-axis along that axis, z=0 at centre of second from bottom row of
    # mPMTs. Ordering of mPMTs increases with phi. Second mPMT is displaced along SM +x axis.

    wall_mpmts = []

    n_col = 16
    for i_row in range(-1, 3):
        loc = [wcte_diameter / 2., 0., i_row * wall_vertical_pitch]
        for j_col in range(n_col):
            phi_angle = 2. * np.pi * j_col / n_col
            rot_phi = Rotation.from_euler('Z', phi_angle)
            rot_loc = rot_phi.apply(loc)
            # rotations of the normal defined by 3 extrinsic rotations
            rot_angles = [np.pi, np.pi / 2., -phi_angle]
            wall_mpmts.append({'kind': 'ME',
                               'loc': rot_loc,
                               'loc_sig': loc_sig,
                               'rot_axes': 'ZYX',
                               'rot_angles': rot_angles,
                               'rot_angles_sig': [rot_angle_sig]*3})

    devices_design['wall'] = wall_mpmts

    def __init__(self, name, container=None, kind='SSM', place_design={}, place_true={}, device_type=MPMT):
        super().__init__(SM, name, container, kind, place_design, place_true)

        # create and place the set of devices
        if device_type == MPMT:
            self.mpmts = self.place_devices(device_type, self.devices_design, kind)
            self.sms = None
        elif device_type == SM:
            self.sms = self.place_devices(device_type, self.devices_design, kind)
            self.mpmts = None

    def get_mpmts(self, mpmt_list):
        # recursive discovery of mpmts in super modules
        if self.mpmts is None:
            for sm in self.sms:
                sm.get_mpmts(mpmt_list)
        else:
            mpmt_list.extend(self.mpmts)
