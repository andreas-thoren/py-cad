import cadquery as cq

ply_thickness = 9
length = 600
width = 300
route_depth = ply_thickness / 2

result = (
 cq.Workplane("XY")
 .box(length, width, ply_thickness-route_depth)
 .faces(">Z")
 .workplane()
 .rect(length-ply_thickness, width-ply_thickness)
 .extrude(route_depth)
)

show_object(result, name="test_part")
