"""
========================================
Visualize bundles and metrics on bundles
========================================

First, let's download some available datasets. Here we are using a dataset
which provides metrics and bundles.
"""

import numpy as np
from dipy.viz import window, actor
from dipy.data import fetch_bundles_2_subjects, read_bundles_2_subjects
from dipy.tracking.streamline import transform_streamlines

fetch_bundles_2_subjects()
dix = read_bundles_2_subjects(subj_id='subj_1', metrics=['fa'],
                              bundles=['cg.left', 'cst.right'])

"""
Store fractional anisotropy.
"""

fa = dix['fa']

"""
Store grid to world transformation matrix.
"""

affine = dix['affine']

"""
Store the cingulum bundle. A bundle is a list of streamlines.
"""

bundle = dix['cg.left']

"""
It happened that this bundle is in world coordinates and therefore we need to
transform it into native image coordinates so that it is in the same coordinate
space as the ``fa`` image.
"""

bundle_native = transform_streamlines(bundle, np.linalg.inv(affine))

"""
Show every streamline with an orientation color
===============================================

This is the default option when you are using ``line`` or ``streamtube``.
"""

renderer = window.Renderer()
renderer.background((1.0, 1.0, 1.0))

stream_actor = actor.halo_line(bundle_native, colors=[1.0, 0.0, 0.0], renderer=renderer)

renderer.set_camera(position=(-176.42, 118.52, 128.20),
                    focal_point=(113.30, 128.31, 76.56),
                    view_up=(0.18, 0.00, 0.98))

renderer.add(stream_actor)

# Uncomment the line below to show to display the window
window.show(renderer, size=(600, 600), reset_camera=False)
