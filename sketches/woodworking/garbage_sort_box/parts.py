import cadquery as cq

def get_bottom_panel(length, width, thickness, route_depth):
    return (
     cq.Workplane("XY")
     .box(length, width, thickness-route_depth)
     .faces(">Z")
     .workplane()
     .rect(length-thickness, width-thickness)
     .extrude(route_depth)
    )

def get_short_side_panel(length, height, thickness):
    return (
     cq.Workplane("XY")
     .box(length, height, thickness)
    )

def get_long_side_panel(length, height, thickness, route_depth):
    groove_offset = length/2 - thickness/2

    return (
        cq.Workplane("XY")
        .box(length, height, thickness)
        .pushPoints([(groove_offset, 0), (-groove_offset, 0)])
        .rect(thickness, height)
        .cutBlind(route_depth)
    )
