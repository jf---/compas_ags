"""An example where the direct solution fails since some edges
in the force diagram are zero length. However, the root finding
approach still works since then the primary unknowns are in
the form diagram.

author: Vedad Alic
email: vedad.alic@construction.lth.se

"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_ags
from compas_ags.diagrams import FormDiagram
from compas_bi_ags.diagrams import ForceDiagram
from compas_ags.viewers import Viewer
from compas_bi_ags.bi_ags import graphstatics

# make form diagram from obj
# make force diagram from form
form = FormDiagram.from_obj(compas_ags.get('zero_fd.obj'))
force = ForceDiagram.from_formdiagram(form)

# set the fixed points
left  = list(form.vertices_where({'x': 0.0, 'y': 0.0}))[0]
right = list(form.vertices_where({'x': 12.0, 'y': 0.0}))[0]
fixed = [left, right]

form.set_fixed(fixed)

e1 = {'v': list(form.vertices_where({'x': 0.0, 'y': 6.0}))[0],
      'u': list(form.vertices_where({'x': 0.0, 'y': 12.0}))[0]}
e2 = {'v': list(form.vertices_where({'x': 6.0, 'y': 6.0}))[0],
      'u': list(form.vertices_where({'x': 6.0, 'y': 12.0}))[0]}
e3 = {'v': list(form.vertices_where({'x': 12.0, 'y': 6.0}))[0],
      'u': list(form.vertices_where({'x': 12.0, 'y': 12.0}))[0]}

#force.set_fixed([2])

# set the magnitude of the applied load
form.set_edge_force(e1['u'], e1['v'], -10.0)
form.set_edge_force(e2['u'], e2['v'], -10.0)
form.set_edge_force(e3['u'], e3['v'], -10.0)


# update the diagrams
graphstatics.form_update_q_from_qind(form)
graphstatics.force_update_from_form(force, form)

# store the original vertex locations
force_key_xyz = {key: force.vertex_coordinates(key) for key in force.vertices()}

# store lines representing the current state of equilibrium
form_lines = []
for u, v in form.edges():
    form_lines.append({
        'start': form.vertex_coordinates(u, 'xy'),
        'end'  : form.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

force_lines = []
for u, v in force.edges():
    force_lines.append({
        'start': force.vertex_coordinates(u, 'xy'),
        'end'  : force.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

#  Display the original configuration
viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(forces_on=False,
                 vertexlabel={key: key for key in form.vertices()},
                 external_on=False,
                 vertexsize=0.2,
                 vertexcolor={key: '#000000' for key in fixed},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())}
)

viewer.draw_force(vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel={uv: index for index, uv in enumerate(force.edges())}
)

viewer.show()

# --------------------------------------------------------------------------
# Begin force diagram manipulation
# --------------------------------------------------------------------------
import compas_bi_ags.bi_ags.rootfinding as rf
import compas_bi_ags.utilities.errorhandler as eh
import numpy as np
xy = np.array(form.xy(), dtype=np.float64).reshape((-1, 2))
_xy = np.array(force.xy(), dtype=np.float64).reshape((-1, 2))

# Select point nearest (1, -8) in the force diagram
_vertex_pos = np.array([[1, -8], ])
idx = 0
l = 1000
for i in range(_xy.shape[0]):
    L = np.sqrt((_xy[i, 0]-_vertex_pos[0, 0])**2 + (_xy[i, 1]-_vertex_pos[0, 1])**2)
    if L < l:
        idx = i
        l = L

# modify the geometry of the force diagram and update form diagram
try:
    force.vertex[idx+1]['x'] += 1.0
    graphstatics.form_update_from_force_direct(form, force)
except eh.SolutionError as e:
    # Root finding solution for when direct solution fails
    force.vertex[idx+1]['x'] -= 1.0
    _xy[idx, 0] += 1.0
    _X_goal = np.vstack((np.asmatrix(_xy[:, 0]).transpose(), np.asmatrix(_xy[:, 1]).transpose()))
    rf.compute_form_from_force_newton(form, force, _X_goal)
# --------------------------------------------------------------------------
# End force diagram manipulation
# --------------------------------------------------------------------------


# display the original configuration
# and the configuration after modifying the force diagram
viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(lines=form_lines,
                 forces_on=False,
                 vertexlabel={key: key for key in form.vertices()},
                 external_on=False,
                 vertexsize=0.2,
                 vertexcolor={key: '#000000' for key in fixed},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())}
)

viewer.draw_force(lines=force_lines,
                  vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel={uv: index for index, uv in enumerate(force.edges())}
)

viewer.show()
