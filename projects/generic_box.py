from primitives.basic_box import get_assembled_box

width = 300
depth = 150
height = 200
thickness = 125
offset = 0

generic_box = get_assembled_box(
    width=width, depth=depth, height=height, thickness=thickness, visual_offset=offset
)
