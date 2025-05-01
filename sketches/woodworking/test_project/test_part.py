import cadquery as cq

def get_result():
    height = 30
    width = 30
    thickness = 5
    diameter = 2

    result = (
     cq.Workplane("XY")
     .box(height, width, thickness)
     .faces(">X")
     .workplane()
     .hole(diameter)
    )
    return result
