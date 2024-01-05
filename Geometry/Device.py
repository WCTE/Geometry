import numpy as np
from scipy import stats
from scipy.spatial.transform import Rotation


class Device:
    """
    Device: A base class for active elements that make up a water Cherenkov detector:

    Class   Device
    -----   ------
    WCD     Water Cherenkov Detector
    SM      Super Module (several mPMTs combined)
    MPMT    Multi-PMT module
    PMT     Photomultiplier Tube
    LED     Light Emitting Diode

    The following are accessible:
        - property dictionaries
            .prop_design: intended properties (read-only)
            .prop_true: properties used in simulation (read-only)
            .prop_est: current property estimates
            .prop_est_sig: standard deviation of property estimators
            .prop_prior: prior property estimates (TBD)
            .prop_prior_sig: standard deviation of priors (TBD)
        - placement dictionaries (for devices that hold other devices, such as mPMTs):
            .place_design: intended placements (read-only)
            .place_true: placement used in simulation (read-only)
            .place_survey: placement as measured by survey
            .place_photo: placement as measured by photogrammetry
            .place_est: current placement estimates
            .place_est_sig: standard deviation of placement estimators
    Misc:
        - "device_type" points to a device class (e.g. PMT or LED)
        - "kind" defines the particular version of the device_type (e.g. 'P1' or 'L2')
        - note that "type" is a reserved word in python - so we avoid using this as a variable name
        - when building a device of a particular kind, the device class
        properties "design_mean, design_scale, design_var" define the design properties
        of the device. These class properties are dictionaries keyed by its "kind"
        - "design_mean" is the mean value
        - "design_scale" is the scale of the variation (standard deviation for normal or gamma,
        half-width for uniform). If 0, there is no variation. Gamma distribution is useful for properties that must be
        positive, yet the standard deviation is a significant fraction of the mean.
        - "design_var" specifies variation type if not Normal. "norm", "gamma", or "uniform"
        - "rot_axes" is the combination of up to 3 Euler rotations, e.g. 'XZX'
        look at scipy.spatial.rotation documentation for conventions
        - "rot_angles" is the corresponding rotation angles in radians
        - "rot_angles_sig" is the corresponding standard deviations of the angles

    """

    def __init__(self, device_type, name, container, kind, place_design, place_true):
        """Constructor"""

        self.prop_design = {}
        self.prop_true = {}
        self.prop_est = {}
        self.prop_est_sig = {}

        self.place_design = {}
        self.place_true = {}
        self.place_survey = {}
        self.place_photo = {}
        self.place_est = {}
        self.place_est_sig = {}

        # force the name to be a string
        self.name = str(name)

        self.container = container
        self.kind = kind

        self.randomly_set_properties(device_type, kind)
        self.set_placement(place_design, place_true)

    def randomly_set_properties(self, device_type, kind):
        """Set the true properties for the device object based on the design distributions"""
        if hasattr(device_type, 'design_mean') and kind in device_type.design_mean:
            self.prop_design = device_type.design_mean[kind]
            truth = {}
            for key in device_type.design_mean[kind]:
                scale = (device_type.design_scale[kind])[key]
                mean = (device_type.design_mean[kind])[key]
                if scale > 0.:
                    var_type = (device_type.design_var[kind]).get(key, 'norm')
                    if var_type == 'uniform':
                        val = stats.uniform.rvs(loc=mean - scale, scale=2. * scale)
                    elif var_type == 'gamma':
                        val = stats.gamma.rvs(a=mean ** 2 / scale ** 2, scale=scale ** 2 / mean, loc=0.)
                    else:
                        val = stats.norm.rvs(loc=mean, scale=scale)
                    truth[key] = val
                else:
                    truth[key] = mean
            self.prop_true = truth

    def get_properties(self, prop_info):
        """Return the properties of the device as a dictionary"""
        # prop_info is a string: either 'true', 'design', or 'est'
        device_prop = getattr(self, 'prop_' + prop_info, None)
        return device_prop

    def set_property(self, prop, value):
        """Set a true property for a device"""
        self.prop_true[prop] = value

    def set_placement(self, place_design, place_true):
        """Save a copy of the device placement information"""
        self.place_design = place_design.copy()
        self.place_true = place_true.copy()

    def place_devices(self, device_type, devices_design, kind):
        """Creates and places sub_devices that make up this device"""
        devices = []
        if kind in devices_design:
            for device in devices_design[kind]:
                device_kind = device['kind']
                place_design = {'loc': device['loc'],
                                'rot_axes': device['rot_axes'],
                                'rot_angles': device['rot_angles']}
                loc_true = []
                for i in range(3):
                    loc_true.append(stats.norm.rvs(device['loc'][i], device['loc_sig'][i]))

                if len(device['rot_axes']) > 1:
                    rot_angles_true = []
                    for i in range(len(device['rot_angles'])):
                        rot_angles_true.append(stats.norm.rvs(device['rot_angles'][i], device['rot_angles_sig'][i]))
                else:
                    rot_angles_true = stats.norm.rvs(device['rot_angles'], device['rot_angles_sig'])

                place_true = {'loc': loc_true, 'rot_axes': device['rot_axes'],
                              'rot_angles': rot_angles_true}
                name = device.get('name', '')
                new_device = device_type(name, self, device_kind, place_design, place_true)
                devices.append(new_device)
        return devices

    def get_placement(self, place_info, device_for_coordinate_system=None):
        """Return the location af device and directions of its x and z axes in the coordinate system
        of the specified container. If the specified container is None, use the coordinate system of
        the top-level container (typically the WCD).
        """

        # define the specified container: the device whose coordinate system we want to use
        specified_container = device_for_coordinate_system
        if specified_container is None:
            specified_container = self
            if self.container is not None:
                while specified_container.container is not None:
                    specified_container = specified_container.container

        # check that if the device has a container the device is within the specified container (at some higher level)
        if self.container is not None:
            the_container = self.container
            inside_container = False
            while the_container is not None:
                if the_container == specified_container:
                    inside_container = True
                    break
                else:
                    the_container = the_container.container
            if not inside_container:
                device_full_name = self.__class__.__name__ + ' ' + self.name
                container_full_name = specified_container.__class__.__name__ + ' ' + specified_container.name
                raise ValueError('Device: ' + device_full_name + ' is not in the specified container: '
                                 + container_full_name + '.')

        if self.container is None or self == specified_container:
            # if a device has no container or if the specified container is itself, then it is located at its origin
            location = [0., 0., 0.]
            direction_x = [1., 0., 0.]
            direction_z = [0., 0., 1.]
        else:
            # get the location and orientation of the device in the container's coordinate system

            # place_info is a string: either 'true', 'design', or 'est'
            # head is the location of the device, tail_x,_z are the ends of vectors of
            # length dist_head aligned with the device's x and z-axes
            device_place = getattr(self, 'place_' + place_info, None)
            if device_place is None:
                raise ValueError('Device: ' + self.__class__.__name__ + ' ' + self.name +
                                 ' has no ' + place_info + 'placement information.')
            head = device_place['loc']
            dist_head = 100.

            rot1 = Rotation.from_euler(device_place['rot_axes'], device_place['rot_angles'])
            x_axis = rot1.apply([1., 0., 0.])
            z_axis = rot1.apply([0., 0., 1.])

            location = head
            direction_x = x_axis
            direction_z = z_axis

            current_container = self.container
            # if the current container is not the specified container, then apply the container's placement
            while current_container != specified_container:
                # apply translation and rotation of current_container
                tail_x = np.add(location, dist_head * direction_x)
                tail_z = np.add(location, dist_head * direction_z)
                container_place = getattr(current_container, 'place_' + place_info, None)
                if container_place is None:
                    raise ValueError('Device: ' + current_container.__class__.__name__ + ' ' + self.name +
                                     ' has no ' + place_info + 'placement information.')
                rot_head = location
                rot_tail_x = tail_x
                rot_tail_z = tail_z
                if 'rot_axes' in container_place:
                    rot2 = Rotation.from_euler(container_place['rot_axes'], container_place['rot_angles'])
                    rot_head = rot2.apply(location)
                    rot_tail_x = rot2.apply(tail_x)
                    rot_tail_z = rot2.apply(tail_z)
                new_direction_x = np.subtract(rot_tail_x, rot_head)
                new_direction_z = np.subtract(rot_tail_z, rot_head)
                norm_x = np.linalg.norm(new_direction_x)
                norm_z = np.linalg.norm(new_direction_z)

                location = np.add(rot_head, container_place.get('loc', [0., 0., 0.]))
                direction_x = np.divide(new_direction_x, norm_x)
                direction_z = np.divide(new_direction_z, norm_z)

                current_container = current_container.container

        return location, direction_x, direction_z

    def get_circle_points(self, n_point, place_info):
        """Return a list of length n_point space points of the circle in the x-y plane"""
        device_prop = getattr(self, 'prop_' + place_info, None)
        radius = device_prop['size'] / 2.
        location, direction_x, direction_z = self.get_placement(place_info)

        # change magnitude of direction_x to device radius
        perp = np.array(direction_x) * radius

        # small rotation about the device z_axis
        rot = Rotation.from_rotvec(2. * np.pi / n_point * np.array(direction_z))
        points = []
        for i in range(n_point):
            points.append(list(np.add(location, perp)))
            perp = rot.apply(perp)

        return points
