from Geometry.Device import Device
from Geometry.MPMT import MPMT
from Geometry.CAMERA import CAMERA
from Geometry.TARGET import TARGET

import numpy as np
from scipy.spatial.transform import Rotation


class SM(Device):
    """A super module consists of a set of either mPMTs or super modules.
    It can also contain cameras and targets. It only has geometry information, no other properties.
    """

    # A dictionary of device kinds and placements in the super module:
    devices_design = {}
    # A dictionary of camera kinds and placements in the super module:
    cameras_design = {}
    # A dictionary of target kinds and placements in the super module:
    targets_design = {}

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

    ssm_cameras = []
    # 2 x 2 rectangular pattern of CAMERAs (for testing):
    for i in np.arange(-0.5, 0.51, 1.0):
        for j in np.arange(-0.5, 0.51, 1.0):
            ssm_cameras.append({'name': str(len(ssm_cameras)), 'kind': 'C',
                                'loc': [600. * i, 600. * (j + 0.5), -100., ],
                                'loc_sig': [1.0, 1.0, 1.0],
                                'rot_axes': 'XZ',
                                'rot_angles': [0., 0.],
                                'rot_angles_sig': [0.01, 0.01]})

    cameras_design['SSM'] = ssm_cameras

    # Super modules that make up the WCTE WCD:
    # The z-axis for each super module is pointing upwards during each super module construction and their initial
    # surveys. Once assembled the WCTE z-axis is aligned with the beam direction

    tb_pitch = 580.  # mm separation of mPMT centres on top and bottom (x and y the same)
    wcte_diameter = 3422.166  # mm separation of mPMT baseplates on opposite barrel locations
    barrel_vertical_pitch = 580.  # mm separation of mPMT centres for rows

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
    y_rots = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.5, 0.5]

    mpmt_kinds = ['ME']*12 + ['FD','ME','FD','ME','FD','ME','FD','ME','ME']

    for i, (offset, y_rot, mpmt_kind) in enumerate(zip(offsets, y_rots, mpmt_kinds)):
        location = offset.copy()
        if i in [12, 14, 16, 18]:
            location[2] = 7.775  # mm offset for FD mPMTs
        bottom_mpmts.append({
            'kind': mpmt_kind,
            'loc': location,
            'loc_sig': loc_sig,
            'rot_axes': 'ZYX',
            'rot_angles': [(y_rot + 0.5) * np.pi, 0., 0.],
            'rot_angles_sig': [rot_angle_sig] * 3
        })

    devices_design['bottom'] = bottom_mpmts

    bottom_cameras = []
    # located at 4 corners of bottom super module
    # they are movable: for now, a typical location is given (same for all)
    camera_radius = 990 * np.sqrt(2)  # typically 990 mm transverse from centre
    camera_z_bot = 200.  # typically 200 mm
    camera_angle = 0.92729  # radians (sin(0.92729) = 0.8)

    for i_cam in range(4):
        # start with a camera located on the bottom endcap x axis
        loc = [camera_radius, 0., camera_z_bot]
        # now rotate it around the bottom endcap z axis
        phi_angle = np.pi / 4. + 2. * np.pi * i_cam / 4
        rot_phi = Rotation.from_euler('Z', phi_angle)
        rot_loc = rot_phi.apply(loc)
        # rotations of the normal defined by 3 rotations
        rot_angles = [phi_angle + np.pi / 2., 0., -camera_angle]

        bottom_cameras.append({'name': str(i_cam), 'kind': 'C',
                               'loc': rot_loc,
                               'loc_sig': [1.0, 1.0, 1.0],
                               'rot_axes': 'ZYX',
                               'rot_angles': rot_angles,
                               'rot_angles_sig': [rot_angle_sig] * 3})

    cameras_design['bottom'] = bottom_cameras

    bottom_targets = []
    # located at a point extending from the support beams of bottom super module
    # they are not to be used to define the coordinate system of the super module
    # instead, they serve as references for determining the placement of the super module after full assembly
    z_inner_top = -20.  # mm of the inner top surface of the support beams
    height_inner_beam = 110.  # mm height of the inner volume of the support beams
    dist_mpmt_to_beam_centre = 267.5 + 45. / 2.  # mm distance from an mPMT to the centre of the support beam
    width_outer_beam = 45.  # mm width of the outer surface of the support beams
    length_beams = [1920., 3030., 3570.]  # lengths of the small, medium, and long beams
    target_extension = 48  # mm extension of the target from the end of the support beams (est by minimizing rms)

    target_z = z_inner_top - height_inner_beam / 2.
    target_xs = [length_beams[2] / 2. + target_extension,
                 length_beams[1] / 2. + target_extension,
                 length_beams[0] / 2. + target_extension,
                 dist_mpmt_to_beam_centre,
                 -dist_mpmt_to_beam_centre,
                 -length_beams[0] / 2. - target_extension,
                 -length_beams[1] / 2. - target_extension,
                 -length_beams[2] / 2. - target_extension,
                 -length_beams[2] / 2. - target_extension,
                 -length_beams[1] / 2. - target_extension,
                 -length_beams[0] / 2. - target_extension,
                 -dist_mpmt_to_beam_centre,
                 dist_mpmt_to_beam_centre,
                 length_beams[0] / 2. + target_extension,
                 length_beams[1] / 2. + target_extension,
                 length_beams[2] / 2. + target_extension]
    target_ys = [dist_mpmt_to_beam_centre,
                 1. * tb_pitch + dist_mpmt_to_beam_centre,
                 2. * tb_pitch + dist_mpmt_to_beam_centre,
                 length_beams[2] / 2. + target_extension,
                 length_beams[2] / 2. + target_extension,
                 2. * tb_pitch + dist_mpmt_to_beam_centre,
                 1. * tb_pitch + dist_mpmt_to_beam_centre,
                 dist_mpmt_to_beam_centre,
                 -dist_mpmt_to_beam_centre,
                 -1. * tb_pitch - dist_mpmt_to_beam_centre,
                 -2. * tb_pitch - dist_mpmt_to_beam_centre,
                 -length_beams[2] / 2. - target_extension,
                 -length_beams[2] / 2. - target_extension,
                 -2. * tb_pitch - dist_mpmt_to_beam_centre,
                 -1. * tb_pitch - dist_mpmt_to_beam_centre,
                 -dist_mpmt_to_beam_centre]

    for i_target in range(16):
        loc = [target_xs[i_target], target_ys[i_target], target_z]

        bottom_targets.append({'name': str(i_target), 'kind': 'T',
                               'loc': loc,
                               'loc_sig': [1.0, 1.0, 1.0],
                               'rot_axes': 'Z',
                               'rot_angles': 0.,
                               'rot_angles_sig': 0.})

    targets_design['bottom'] = bottom_targets

    # Top super module:
    ###################
    # Constructed with the mPMTs z-axes pointing downwards, unlike the bottom super module.
    # Second mPMT is displaced along SM +x axis.

    top_mpmts = []

    # as built:
    y_rots = [0, 0.5, 0.5, 1.5, 1.5, 1.5, 0., 1.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 0., 1.5, 1.5, 1.5, 1.5, 0.5, 0.5]

    for offset, y_rot in zip(offsets, y_rots):
        location = offset
        top_mpmts.append({
            'kind': 'ME',
            'loc': location,
            'loc_sig': loc_sig,
            'rot_axes': 'ZYX',
            'rot_angles': [(y_rot - 0.5) * np.pi, np.pi, 0.],
            'rot_angles_sig': [rot_angle_sig] * 3
        })

    devices_design['top'] = top_mpmts

    top_cameras = []
    # located at 4 corners of top super module
    camera_z_top = 270.  # typically 270 mm

    for i_cam in range(4):
        # start with a camera located on the bottom endcap x axis
        loc = [camera_radius, 0., -camera_z_top]
        # now rotate it around the bottom endcap z axis
        phi_angle = np.pi / 4. + 2. * np.pi * i_cam / 4
        rot_phi = Rotation.from_euler('Z', phi_angle)
        rot_loc = rot_phi.apply(loc)
        # rotations of the normal defined by 2 extrinsic rotations
        rot_angles = [phi_angle + np.pi / 2., 0., -np.pi / 2. - camera_angle]

        top_cameras.append({'name': str(i_cam + 4), 'kind': 'C',
                            'loc': rot_loc,
                            'loc_sig': [1.0, 1.0, 1.0],
                            'rot_axes': 'ZYX',
                            'rot_angles': rot_angles,
                            'rot_angles_sig': [rot_angle_sig] * 3})

    cameras_design['top'] = top_cameras

    top_targets = []
    # located at a point extending from the support beams of bottom super module
    # they are not to be used to define the coordinate system of the super module
    # instead, they serve as references for determining the placement of the super module after full assembly
    z_inner_top = -10.  # mm of the inner top surface of the support beams (different from bottom)

    target_z = z_inner_top - height_inner_beam / 2.

    for i_target in range(16):
        loc = [target_xs[i_target], target_ys[i_target], target_z]

        top_targets.append({'name': str(i_target), 'kind': 'T',
                            'loc': loc,
                            'loc_sig': [1.0, 1.0, 1.0],
                            'rot_axes': 'Z',
                            'rot_angles': 0.,
                            'rot_angles_sig': 0.})

    targets_design['top'] = top_targets

    # Barrel super module:
    ####################
    # Origin on cylinder axis, z-axis along that axis, z=0 at centre of second from bottom row of
    # mPMTs. Ordering of mPMTs increases with phi. Second mPMT is displaced along SM +x axis.

    barrel_mpmts = []

    n_col = 16
    for i_row in range(-1, 3):
        loc = [wcte_diameter / 2., 0., i_row * barrel_vertical_pitch]
        for j_col in range(n_col):
            phi_angle = 2. * np.pi * j_col / n_col
            rot_phi = Rotation.from_euler('Z', phi_angle)
            rot_loc = rot_phi.apply(loc)
            # rotations of the normal defined by 3 extrinsic rotations
            rot_angles = [np.pi, np.pi / 2., -phi_angle]
            barrel_mpmts.append({'kind': 'ME',
                                 'loc': rot_loc,
                                 'loc_sig': loc_sig,
                                 'rot_axes': 'ZYX',
                                 'rot_angles': rot_angles,
                                 'rot_angles_sig': [rot_angle_sig] * 3})

    devices_design['barrel'] = barrel_mpmts

    # Super modules that make up the IWCD WCD:
    # The z-axis for each super module is pointing upwards.
    # Once assembled, the IWCD z-axis is in horizontal, closely aligned with the beam direction

    iwcd_tb_pitch = 830.  # mm separation of mPMT centres on top and bottom (x and y the same)
    iwcd_bot_centre_extra_x = 15 # mm extra x offset of nearest to centre mPMTs relative to centre in x
    iwcd_bot_centre_extra_y = 15 # mm extra y offset of nearest to centre mPMTs relative to centre in y
    iwcd_diameter = 3661.87*2  # mm separation of mPMT baseplates on opposite barrel locations
    iwcd_barrel_vertical_pitch_11 = 720.  # mm separation of mPMT centres for rows within a supermodule (11 row version)
    iwcd_barrel_vertical_pitch_10 = 800.  # mm separation of mPMT centres for rows within a supermodule (11 row version)
    iwcd_barrel_vertical_pitch_extra = 10.  # mm separation between supermodules
    iwcd_barrel_z0 = -7230/2. # mm z coordinate of the mPMTs in the lowest row of the barrel supermodule

    loc_sig = [5.0, 5.0, 5.0]  # mm positioning accuracy
    rot_angle_sig = 0.05  # radians

    # Bottom super module:
    ######################
    # Origin is the centre of the set of the mPMT origins. z-axis coincides with that of the mPMTs.
    # Ordering of MPTs spirals with +phi.

    iwcd_bottom_mpmts = []

    # Start with 4 mPMTs around the centre of bottom
    offsets = []

    offs_x = [-iwcd_tb_pitch / 2 - iwcd_bot_centre_extra_x, iwcd_tb_pitch / 2 + iwcd_bot_centre_extra_x]
    offs_y = [-iwcd_tb_pitch / 2 - iwcd_bot_centre_extra_y, iwcd_tb_pitch / 2 + iwcd_bot_centre_extra_y]
    for i in range(4):
        offset = [offs_x[[1, 0, 0, 1][i]], offs_y[[1, 1, 0, 0][i]], 0.]
        offsets.append(offset)

    # Next 12 mPMTs in a square around the first 4
    offs_x = [-iwcd_tb_pitch * 3/2 - iwcd_bot_centre_extra_x, -iwcd_tb_pitch / 2 - iwcd_bot_centre_extra_x,
                iwcd_tb_pitch / 2 + iwcd_bot_centre_extra_x, iwcd_tb_pitch * 3/2 + iwcd_bot_centre_extra_x]
    offs_y = [-iwcd_tb_pitch * 3/2 - iwcd_bot_centre_extra_y, -iwcd_tb_pitch / 2 - iwcd_bot_centre_extra_y,
                iwcd_tb_pitch / 2 + iwcd_bot_centre_extra_y, iwcd_tb_pitch * 3/2 + iwcd_bot_centre_extra_y]
    for i in range(12):
        offset = [offs_x[[3,3,2,1,0,0,0,0,1,2,3,3][i]], offs_y[[2,3,3,3,3,2,1,0,0,0,0,1][i]], 0.]
        offsets.append(offset)

    # Next 20 mPMTs in a larger square around the first 16
    offs_x = [-iwcd_tb_pitch * 5/2 - iwcd_bot_centre_extra_x, -iwcd_tb_pitch * 3/2 - iwcd_bot_centre_extra_x,
                -iwcd_tb_pitch / 2 - iwcd_bot_centre_extra_x,
                iwcd_tb_pitch / 2 + iwcd_bot_centre_extra_x, iwcd_tb_pitch * 3/2 + iwcd_bot_centre_extra_x,
                iwcd_tb_pitch * 5/2 + iwcd_bot_centre_extra_x]
    offs_y = [-iwcd_tb_pitch * 5/2 - iwcd_bot_centre_extra_y, -iwcd_tb_pitch * 3/2 - iwcd_bot_centre_extra_y,
                -iwcd_tb_pitch / 2 - iwcd_bot_centre_extra_y,
                iwcd_tb_pitch / 2 + iwcd_bot_centre_extra_y, iwcd_tb_pitch * 3/2 + iwcd_bot_centre_extra_y,
                iwcd_tb_pitch * 5/2 + iwcd_bot_centre_extra_y]
    for i in range(20):
        offset = [offs_x[[5,5,5,4,3,2,1,0,0,0,0,0,0,1,2,3,4,5,5,5][i]],
                  offs_y[[3,4,5,5,5,5,5,5,4,3,2,1,0,0,0,0,0,0,1,2][i]], 0.]
        offsets.append(offset)

    # Next there are 4 sets of 4 mPMTs in a partially completed square around the first 36
    offs_x = [-iwcd_tb_pitch * 7/2 - iwcd_bot_centre_extra_x, -iwcd_tb_pitch * 3/2 - iwcd_bot_centre_extra_x,
                -iwcd_tb_pitch / 2 - iwcd_bot_centre_extra_x, iwcd_tb_pitch / 2 + iwcd_bot_centre_extra_x,
                iwcd_tb_pitch * 3/2 + iwcd_bot_centre_extra_x, iwcd_tb_pitch * 7/2 + iwcd_bot_centre_extra_x]
    offs_y = [-iwcd_tb_pitch * 7/2 - iwcd_bot_centre_extra_y, -iwcd_tb_pitch * 3/2 - iwcd_bot_centre_extra_y,
                -iwcd_tb_pitch / 2 - iwcd_bot_centre_extra_y, iwcd_tb_pitch / 2 + iwcd_bot_centre_extra_y,
                iwcd_tb_pitch * 3/2 + iwcd_bot_centre_extra_y, iwcd_tb_pitch * 7/2 + iwcd_bot_centre_extra_y]
    for i in range(16):
        offset = [offs_x[[5,5,4,3,2,1,0,0,0,0,1,2,3,4,5,5][i]],
                  offs_y[[3,4,5,5,5,5,4,3,2,1,0,0,0,0,1,2][i]], 0.]
        offsets.append(offset)

    # rotate mPMTs to put feed-throughs in correct orientations... pi multiplier starting at #0
    #y_rots = [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
    #y_rots = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.5, 0.5]

    y_rots = [0] * len(offsets)

    for i, (offset, y_rot) in enumerate(zip(offsets, y_rots)):
        location = offset.copy()
        iwcd_bottom_mpmts.append({
            'kind': 'ME',
            'loc': location,
            'loc_sig': loc_sig,
            'rot_axes': 'ZYX',
            'rot_angles': [(y_rot + 0.5) * np.pi, 0., 0.],
            'rot_angles_sig': [rot_angle_sig] * 3
        })

    devices_design['iwcd_bottom'] = iwcd_bottom_mpmts

    # Top IWCD super module:
    #######################
    # Defined with the mPMTs z-axes pointing downwards, unlike the bottom super module.
    # Fifth mPMT is displaced along SM +x axis.

    iwcd_top_mpmts = []

    # as built:
    #y_rots = [0, 0.5, 0.5, 1.5, 1.5, 1.5, 0., 1.5, 0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 0., 1.5, 1.5, 1.5, 1.5, 0.5, 0.5]
    y_rots = [0] * len(offsets)

    for offset, y_rot in zip(offsets, y_rots):
        location = offset
        iwcd_top_mpmts.append({
            'kind': 'ME',
            'loc': location,
            'loc_sig': loc_sig,
            'rot_axes': 'ZYX',
            'rot_angles': [(y_rot - 0.5) * np.pi, np.pi, 0.],
            'rot_angles_sig': [rot_angle_sig] * 3
        })

    devices_design['iwcd_top'] = iwcd_top_mpmts

    # IWCD Barrel super module:
    ##########################
    # Origin on cylinder axis, z-axis along that axis, z=0 at midpoint of the bottom and top rows of
    # mPMTs. Ordering of mPMTs increases with phi.
    # Consider a staggered pattern of mPMTs to compare performance

    iwcd_smb_ys = [-325, 571.5] # mm y coordinates of the two columns of mPMTs in the barrel supermodule
    for barrel_name in ['iwcd_barrel', 'iwcd_barrel_staggered', 'iwcd_barrel_10row']:
        iwcd_barrel_vertical_pitch = iwcd_barrel_vertical_pitch_11
        n_row = 11
        n_gap_pattern = [0,0,0,1,1,1,2,2,2,3,3] # number of gaps in the row of mPMTs (between supermodules)
        if barrel_name == 'iwcd_barrel_10row':
            iwcd_barrel_vertical_pitch = iwcd_barrel_vertical_pitch_10
            n_row = 10
            n_gap_pattern = [0,0,1,1,1,2,2,2,3,3] # number of gaps in the row of mPMTs (between supermodules)

        iwcd_barrel_mpmts = []

        n_col = 12 # number of barrel supermodules in the IWCD barrel
        for i_row in range(n_row):
            n_gaps = n_gap_pattern[i_row] # number of gaps in the row of mPMTs (between supermodules)
            z = iwcd_barrel_z0 + i_row * iwcd_barrel_vertical_pitch + n_gaps * iwcd_barrel_vertical_pitch_extra
            for j_col in range(n_col):
                for iloc in range(2):
                    loc = [iwcd_diameter / 2., iwcd_smb_ys[iloc], z]
                    if barrel_name == 'iwcd_barrel_staggered' and i_row%2 == 1:
                        loc[1] = -iwcd_smb_ys[1-iloc]
                    phi_angle = 2. * np.pi * j_col / n_col + np.pi/12 # fix incorrect rotation of supermodules
                    rot_phi = Rotation.from_euler('Z', phi_angle)
                    rot_loc = rot_phi.apply(loc)
                    # rotations of the normal defined by 3 extrinsic rotations
                    rot_angles = [np.pi, np.pi / 2., -phi_angle]
                    iwcd_barrel_mpmts.append({'kind': 'ME',
                                         'loc': rot_loc,
                                         'loc_sig': loc_sig,
                                         'rot_axes': 'ZYX',
                                         'rot_angles': rot_angles,
                                         'rot_angles_sig': [rot_angle_sig] * 3})

        devices_design[barrel_name] = iwcd_barrel_mpmts

    def __init__(self, name, container=None, kind='SSM', place_design={}, place_true={}, device_type=MPMT):
        super().__init__(SM, name, container, kind, place_design, place_true)

        # create and place the set of devices
        if device_type == MPMT:
            self.mpmts = self.place_devices(device_type, self.devices_design, kind)
            self.sms = None
        elif device_type == SM:
            self.sms = self.place_devices(device_type, self.devices_design, kind)
            # collect all the mpmts in the WCD
            self.mpmts = []
            for sm in self.sms:
                sm.get_mpmts(self.mpmts)
            # give each mpmt a unique name
            for i, mpmt in enumerate(self.mpmts):
                mpmt.name = str(i)

        # create and place the set of cameras
        self.cameras = None
        if self.cameras_design.get(kind, None) is not None:
            self.cameras = self.place_devices(CAMERA, self.cameras_design, kind)

        # create and place the set of targets
        self.targets = None
        if self.targets_design.get(kind, None) is not None:
            self.targets = self.place_devices(TARGET, self.targets_design, kind)

    def get_mpmts(self, mpmt_list):
        # recursive discovery of mpmts in super modules
        if self.mpmts is None:
            for sm in self.sms:
                sm.get_mpmts(mpmt_list)
        else:
            mpmt_list.extend(self.mpmts)

    def get_cameras(self, camera_list):
        # recursive discovery of cameras in super modules
        if self.sms is not None:
            for sm in self.sms:
                sm.get_cameras(camera_list)
        else:
            if self.cameras is not None:
                camera_list.extend(self.cameras)

    def get_targets(self, target_list):
        # recursive discovery of targets in super modules
        if self.sms is not None:
            for sm in self.sms:
                sm.get_targets(target_list)
        else:
            if self.targets is not None:
                target_list.extend(self.targets)
