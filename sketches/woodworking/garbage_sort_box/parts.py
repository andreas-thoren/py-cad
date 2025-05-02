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

def get_long_side_panel(length, height, thickness, route_depth, invert_grooves=False):
    groove_offset = length/2 - thickness/2
    groove_face = ">Y" if invert_grooves else "<Y"
    divider_width = 50

    return (
        cq.Workplane("XZ")
        .box(length, height, thickness)
        .faces(groove_face)
        .workplane()
        .pushPoints([(groove_offset, 0), (-groove_offset, 0)])
        .rect(thickness, height)
        .cutBlind(-route_depth)
        .faces(groove_face)
        .workplane()
        .moveTo(0, (height-divider_width)/2)
        .rect(thickness, divider_width)
        .cutBlind(-route_depth)
    )
