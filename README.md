# Geometry
This is a python library for specifying locations and orientations of devices that make up water Cherenkov
detectors (WCDs) based on multi-PMT modules (mPMTs). Devices, derived from the Device class, can contain other devices
which are placed according to the coordinate system of its container. For example PMT placements are specified in
the coordinate system of the mPMT they are contained in, and mPMT placements are specified in the coordinate system
of the WCD (or Super Module) they are contained in. The WCD can be placed in a global coordinate system, or it can
be used to define the global coordinate system.

The table below shows the active elements, which are classes that inherit from the `Device` class:

| Class | Device                                | Kinds currently implemented                             |
|:------|:--------------------------------------|:--------------------------------------------------------|
| WCD   | Water Cherenkov Detector              | WCTE: full detector                                     |
| SM    | Super Module (several mPMTs combined) | SSM: simple super module as basis of mPMT test setup    |
|       |                                       | bottom, top, wall : super modules that make up the WCTE |
| MPMT  | Multi-PMT module                      | ME: ex-situ, MI: in-situ, MR: rectangular (for testing) |
| PMT   | Photomultiplier Tube                  | P3: normal 3 inch PMT                                   |
| LED   | Light Emitting Diode                  | LD: diffuse, LC: collimated                             |

To allow extended functionality beyond geometry, the `Device` class also includes properties.
Class dictionaries of dictionaries store design properties of different kinds of devices, first indexed by the 
specific "kind" of that device, then by property name. 
Separate dictionaries store the mean, scale of variations, and distribution of variations for these design properties: 
Device.design_mean, Device.design_scale, and Device.design_var.
The third column in the table above shows the kinds of devices that are currently implemented and the first one 
indicated is the default kind for that device.

When instantiating a device, the object is assigned "true" properties that are drawn from the design distributions for 
that kind of device.
The (true, design, or estimated) properties of a device can be accessed using the `get_properties` method with the 
desired kind of properties as an argument ('true', 'design', or 'est').

It is best to not change the design properties of a device kind after instantiating any devices of that kind, as that
would cause you to have devices with different design properties of the same kind.
It is possible to change the true properties of a device after it has been instantiated.

```python  
    >>> from Geometry.PMT import PMT
    >>> test_pmt = PMT('test_pmt', kind='P3')
    >>> design = test_pmt.get_properties('design')
    >>> for key in design:
            print(key, design[key], PMT.design_desc[key])
        
    fov 1.0 radian field of view (cone half angle)
    size 75 mm diameter
    qe 0.5 quantum efficiency
    gain 2.1 mV per photoelectron
    delay 4.0 ns mean delay of signal wrt pulse
    tts 1.0 ns transit time spread: standard deviation of transit delay

    >>> test_pmt.get_properties('true')
    {'fov': 0.9995023747534968, 'size': 74.78823666698443, 'qe': 0.5153263649689654, 'gain': 2.1558566901071807, 'delay': 3.959916692439508, 'tts': 0.9006637837841815}
    
    >>> PMT.design_mean['P3']['delay'] = 100. # changing the design properties of a device kind after one has already been instantiated as test_pmt (not recommended)
    >>> PMT.design_scale['P3']['delay'] = 10.
    >>> test_pmt2 = PMT('test_pmt2') # instantiating a new 'P3' PMT will use the new design properties
    >>> print(test_pmt2.get_properties('design')['delay'], test_pmt2.get_properties('true')['delay'])
    100.0 95.13212911052935
    >>> print('test_pmt:', test_pmt.get_properties('design')['delay'], test_pmt.get_properties('true')['delay']) # design value for P3 type PMTs has changed after test_pmt was instantiated
    test_pmt: 100.0 4.6118416289470705

    >>> test_pmt.set_property('delay', 200.)
    print('test_pmt:', test_pmt.get_properties('design')['delay'], test_pmt.get_properties('true')['delay'])
    test_pmt: 100.0 200.0
```

Instantiating a device that contains other devices will also instantiate those devices, and so on recursively.
Such devices have placement dictionaries that specify the locations and orientations of the devices they contain.
The locations and orientations of the device can be accessed using the `get_placement` method with arguments
specifying the desired kind of placement information as an argument ('true', 'design', or 'est') and the device whose
coordinate system you want to use as a reference.

```python
    >>> from Geometry.MPMT import MPMT
    >>> test_mpmt = MPMT('test_mpmt', kind='ME')
    >>> pmt1 = test_mpmt.pmts[1]
    >>> placement = pmt1.get_placement('design', test_mpmt)
    >>> for key in placement:
    ...     print(key, placement[key])
    location [  0.          95.29664979 232.558     ]
    direction_x [1. 0. 0.]
    direction_z [0.         0.29265287 0.95621875]

    >>> from Geometry.WCD import WCD
    >>> wcte = WCD('wcte', kind='WCTE')
    >>> pmt_43_1 = wcte.mpmts[43].pmts[1]
    >>> placement = pmt_43_1.get_placement('design', wcte)
    >>> for key in placement:
    ...     print(key, placement[key])
    location [ 1.11285996e+03  1.92505783e-13 -9.78090146e+02]
    direction_x [ 0. -1.  0.]
    direction_z [-4.69211932e-01 -3.12164882e-16  8.83085592e-01]
```

Other WCD or Supermodule designs can be defined by extending the WCD or SM classes and adding to the 
design dictionaries.

Additional functionality for the devices can be incorporated by extending the device classes. The TimingCalib package
is an example of this. (TODO: revise TimingCalib package to use this package).

TODO: 
 * add examples to draw pictures of devices and their placements
 * show how to incorporate survey data

