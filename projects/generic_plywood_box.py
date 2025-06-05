from py_cad.primitives.plywood_box.project_data import BoxDimensionData

# Project dimensions
BOX_X = 300
BOX_Y = 200
BOX_Z = 200
PLY_THICKNESS = 9
ROUTE_DEPTH = PLY_THICKNESS / 2

BOX_DIMENSIONS = BoxDimensionData(
    (BOX_X, BOX_Y, BOX_Z), mat_thickness=PLY_THICKNESS, route_depth=ROUTE_DEPTH
)
