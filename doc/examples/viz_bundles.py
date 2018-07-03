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

stream_actor = actor.line(bundle_native)

stream_actor.GetProperty().SetLineWidth(5)
stream_actor.GetProperty().SetRenderLinesAsTubes(1)

renderer.set_camera(position=(-176.42, 118.52, 128.20),
                    focal_point=(113.30, 128.31, 76.56),
                    view_up=(0.18, 0.00, 0.98))

renderer.add(stream_actor)

# Uncomment the line below to show to display the window
window.show(renderer, size=(600, 600), reset_camera=False)
# window.record(renderer, out_path='bundle1.png', size=(600, 600))

"""
.. figure:: bundle1.png
   :align: center

   One orientation color for every streamline.

You may wonder how we knew how to set the camera. This is very easy. You just
need to run ``window.show`` once see how you want to see the object and then
close the window and call the ``camera_info`` method which prints the position,
focal point and view up vectors of the camera.
"""

renderer.camera_info()

"""
Show every point with a value from a volume with default colormap
=================================================================

Here we will need to input the ``fa`` map in ``streamtube`` or ``line``.
"""

renderer.clear()
stream_actor2 = actor.line(bundle_native, fa, linewidth=0.1)

stream_actor2.GetProperty().SetLineWidth(5)
# stream_actor2.GetProperty().SetRenderLinesAsTubes(1)

stream_mapper = stream_actor2.GetMapper()

stream_mapper.SetGeometryShaderCode(
    "//VTK::System::Dec\n"

    "// Template for the polydata mappers geometry shader\n"

    "// VC position of this fragment\n"
    "//VTK::PositionVC::Dec\n"

    "// primitiveID\n"
    "//VTK::PrimID::Dec\n"

    "// optional color passed in from the vertex shader, vertexColor\n"
    "//VTK::Color::Dec\n"

    "// optional surface normal declaration\n"
    "//VTK::Normal::Dec\n"

    "// extra lighting parameters\n"
    "//VTK::Light::Dec\n"

    "// Texture coordinates\n"
    "//VTK::TCoord::Dec\n"

    "// picking support\n"
    "//VTK::Picking::Dec\n"

    "// Depth Peeling Support\n"
    "//VTK::DepthPeeling::Dec\n"

    "// clipping plane vars\n"
    "//VTK::Clip::Dec\n"

    "// the output of this shader\n"
    "//VTK::Output::Dec\n"

    "uniform vec2 lineWidthNVC;\n"

    "layout(lines) in;\n"
    "layout(triangle_strip, max_vertices = 4) out;\n"

    "void main()\n"
    "{\n"
    "   // compute the lines direction\n"
    "   vec2 normal = normalize(\n"
    "       gl_in[1].gl_Position.xy/gl_in[1].gl_Position.w -\n"
    "       gl_in[0].gl_Position.xy/gl_in[0].gl_Position.w);\n"

    "   // rotate 90 degrees\n"
    "   normal = vec2(-1.0*normal.y,normal.x);\n"

    "   //VTK::Normal::Start\n"

    "   for (int j = 0; j < 4; j++)\n"
    "   {\n"
    "       int i = j/2;\n"

    "       //VTK::PrimID::Impl\n"

    "       //VTK::Clip::Impl\n"

    "       //VTK::Color::Impl\n"

    "       //VTK::Normal::Impl\n"

    "       //VTK::Light::Impl\n"

    "       //VTK::TCoord::Impl\n"

    "       //VTK::DepthPeeling::Impl\n"

    "       //VTK::Picking::Impl\n"

    "       // VC position of this fragment\n"
    "       //VTK::PositionVC::Impl\n"

    "       gl_Position = vec4(\n"
    "           gl_in[i].gl_Position.xy + (lineWidthNVC*normal)*((j+1)%2 - 0.5)*gl_in[i].gl_Position.w,\n"
    "           gl_in[i].gl_Position.z,\n"
    "           gl_in[i].gl_Position.w);\n"
    "       EmitVertex();\n"
    "   }\n"
    "   EndPrimitive();\n"
    "}"
)

stream_mapper.SetFragmentShaderCode(
    "//VTK::System::Dec\n"  # always start with this line
    "//VTK::Output::Dec\n"  # always have this line in your FS
    "varying vec3 normalVCVSOutput;\n"
    "uniform vec3 diffuseColorUniform;\n"
    "void main () {\n"
    "  float df = max(0.0, normalVCVSOutput.z);\n"
    "  float sf = pow(df, 20.0);\n"
    "  vec3 diffuse = df * diffuseColorUniform;\n"
    "  vec3 specular = sf * vec3(0.4,0.4,0.4);\n"
    "  gl_FragData[0] = vec4(1.0, 0.0, 0.0, 1.0);\n"
    "}\n"
)


"""
We can also show the scalar bar.
"""

bar = actor.scalar_bar()

renderer.add(stream_actor2)
# renderer.add(bar)

window.show(renderer, size=(600, 600), reset_camera=False)
# window.record(renderer, out_path='bundle2.png', size=(600, 600))

"""
.. figure:: bundle2.png
   :align: center

   Every point with a color from FA.

Show every point with a value from a volume with your colormap
==============================================================

Here we will need to input the ``fa`` map in ``streamtube``
"""

renderer.clear()

hue = [0.0, 0.0]  # red only
saturation = [0.0, 1.0]  # white to red

lut_cmap = actor.colormap_lookup_table(hue_range=hue,
                                       saturation_range=saturation)

stream_actor3 = actor.line(bundle_native, fa, linewidth=0.1,
                           lookup_colormap=lut_cmap)
bar2 = actor.scalar_bar(lut_cmap)

renderer.add(stream_actor3)
renderer.add(bar2)

# window.show(renderer, size=(600, 600), reset_camera=False)
# window.record(renderer, out_path='bundle3.png', size=(600, 600))

"""
.. figure:: bundle3.png
   :align: center

   Every point with a color from FA using a non default colormap.


Show every bundle with a specific color
========================================

You can have a bundle with a specific color. In this example, we are chosing
orange.
"""

renderer.clear()
stream_actor4 = actor.line(bundle_native, (1., 0.5, 0), linewidth=0.1)

renderer.add(stream_actor4)

# window.show(renderer, size=(600, 600), reset_camera=False)
# window.record(renderer, out_path='bundle4.png', size=(600, 600))

"""
.. figure:: bundle4.png
   :align: center

   Entire bundle with a specific color.

Show every streamline of a bundle with a different color
========================================================

Let's make a colormap where every streamline of the bundle is colored by its
length.
"""

renderer.clear()

from dipy.tracking.streamline import length

lengths = length(bundle_native)

hue = [0.5, 0.5]  # red only
saturation = [0.0, 1.0]  # black to white

lut_cmap = actor.colormap_lookup_table(
    scale_range=(lengths.min(), lengths.max()),
    hue_range=hue,
    saturation_range=saturation)

stream_actor5 = actor.line(bundle_native, lengths, linewidth=0.1,
                           lookup_colormap=lut_cmap)

renderer.add(stream_actor5)
bar3 = actor.scalar_bar(lut_cmap)

renderer.add(bar3)

# window.show(renderer, size=(600, 600), reset_camera=False)
# window.record(renderer, out_path='bundle5.png', size=(600, 600))

"""
.. figure:: bundle5.png
   :align: center
   **Color every streamline by the length of the streamline **


Show every point of every streamline with a different color
============================================================

In this case in which we want to have a color per point and per streamline,
we can create a list of the colors to correspond to the list of streamlines
(bundles). Here in ``colors`` we will insert some random RGB colors.
"""

renderer.clear()

colors = [np.random.rand(*streamline.shape) for streamline in bundle_native]

stream_actor6 = actor.line(bundle_native, colors, linewidth=0.2)

renderer.add(stream_actor6)

# window.show(renderer, size=(600, 600), reset_camera=False)
# window.record(renderer, out_path='bundle6.png', size=(600, 600))

"""
.. figure:: bundle6.png
   :align: center

   Random colors per points per streamline.

In summary, we showed that there are many useful ways for visualizing maps
on bundles.

"""
