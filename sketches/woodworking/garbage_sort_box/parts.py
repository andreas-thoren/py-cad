import cadquery as cq

def get_bottom_panel(length, width, thickness, route_depth):
    bottom_panel = (
     cq.Workplane("XY")
     .box(length, width, thickness-route_depth)
     .faces(">Z")
     .workplane()
     .rect(length-thickness, width-thickness)
     .extrude(route_depth)
    )
    return bottom_panel

def get_long_side_panel(length, height, thickness, route_depth):
    long_side_panel = (
     cq.Workplane("XY")
     .box(length, height, thickness-route_depth)
     .faces(">Z")
     .workplane()
     .center(0, thickness/2)
     .rect(length, height-thickness)
     .extrude(route_depth)
    )
    return long_side_panel