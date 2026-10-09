"""Schematic 3-D torso from the user's six-column sketch, not a cap montage."""
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class TorsoLayout:
    back_mapping: str = 'C behind A'
    top_to_bottom: bool = False  # Outer columns: low at bottom; middle reverses.
    front_b_on_right: bool = False  # B/D = person's right, front-screen left.

    def __post_init__(self):
        if self.back_mapping not in ('C behind A', 'C behind B'):
            raise ValueError('Unknown back mapping')
        if not isinstance(self.top_to_bottom, bool) or not isinstance(self.front_b_on_right, bool):
            raise ValueError('Numbering direction must be boolean')

    def positions(self):
        output = {}
        for bank in 'ABCD':
            side = 1 if bank == 'A' else -1 if bank == 'B' else (
                1 if (bank == 'C') == (self.back_mapping == 'C behind A') else -1)
            if self.front_b_on_right:
                side *= -1
            face = -1 if bank in 'AB' else 1
            for first, last, fraction in ((1, 10, .20), (11, 21, .49), (22, 32, .78)):
                for row, number in enumerate(range(first, last+1)):
                    amount = row/(last-first)
                    # Serpentine wiring: the 11-21 strip runs opposite to its
                    # neighbouring 1-10 and 22-32 strips (the user's sketch).
                    if first == 11:
                        amount = 1-amount
                    if not self.top_to_bottom:
                        amount = 1-amount
                    z = 2.13-1.85*amount
                    width, depth = torso_radius(z)
                    x = side*fraction*width
                    y = face*(depth*math.sqrt(1-fraction*fraction)+.028)
                    output[f'{bank}{number}'] = dict(point=(x, y, z),
                        normal=(side*fraction/width, face*math.sqrt(1-fraction*fraction)/depth, 0),
                        face='Front' if face < 0 else 'Back', bank=bank)
        return output


def torso_radius(z):
    levels = (0, .45, 1.2, 2.12, 2.33, 2.55, 2.68)
    return (float(np.interp(z, levels, (.83, .78, .91, 1.04, .95, .24, .24))),
            float(np.interp(z, levels, (.36, .37, .42, .43, .33, .23, .23))))


def torso_mesh():
    """Low-poly trunk and short upper arms, returned as ordered vertices."""
    faces = []
    zs = sorted(set(np.linspace(0, 2.68, 18)) | {2.12, 2.33, 2.55})
    angles = np.linspace(0, 2*math.pi, 33)
    rings = [[(torso_radius(z)[0]*math.cos(a), torso_radius(z)[1]*math.sin(a), z)
              for a in angles] for z in zs]
    for lower, upper in zip(rings, rings[1:]):
        faces.extend([[lower[i], lower[i+1], upper[i+1], upper[i]] for i in range(32)])
    faces.append(list(reversed(rings[0][:-1])))
    faces.append(rings[-1][:-1])
    for side in (-1, 1):
        start, end = np.array((side*.99, 0, 2.16)), np.array((side*1.29, 0, .78))
        axis = end-start; axis /= np.linalg.norm(axis)
        first = np.array((0,1,0)); second = np.cross(axis,first)
        arm_rings = []
        for fraction, radius in ((0,.20),(.25,.21),(.7,.17),(1,.15)):
            centre = start+fraction*(end-start)
            arm_rings.append([tuple(centre+radius*(math.cos(a)*first+math.sin(a)*second))
                              for a in np.linspace(0,2*math.pi,17)])
        for a,b in zip(arm_rings,arm_rings[1:]):
            faces.extend([[a[i],a[i+1],b[i+1],b[i]] for i in range(16)])
        faces.append(arm_rings[-1][:-1])
    return faces


def project(point, yaw=0., pitch=6.):
    """Orthographic camera. Front x>0 is viewer-right; back reverses naturally."""
    x,y,z = point
    a,b = math.radians(yaw), math.radians(pitch)
    horizontal = x*math.cos(a)+y*math.sin(a)
    near = x*math.sin(a)-y*math.cos(a)
    return horizontal, z*math.cos(b)-near*math.sin(b), z*math.sin(b)+near*math.cos(b)


def visible(normal, yaw, pitch):
    return project(normal,yaw,pitch)[2] > .02


MESH = torso_mesh()
