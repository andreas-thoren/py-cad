import cadquery as cq

# Create a simple box
box = cq.Workplane("XY").box(2, 2, 2)

# Create an edge (for demo, we just make a circle edge)
circle_edge = cq.Edge.makeCircle(radius=10)

# Set up the assembly
assy = cq.Assembly()

# Add the objects to the assembly with names
assy.add(circle_edge, name="circle")
assy.add(box, name="red_box", color=cq.Color("red"))
assy.add(box, name="green_box", color=cq.Color("green"))
assy.add(box, name="blue_box", color=cq.Color("blue"))

# --- 1️⃣ Constrain by center between two named parts
# assy.constrain("circle", "red_box", "Point")
try:
    assy.constrain("circle", "red_box", "Point")
except KeyError as exc:
    pass

print(len(assy.constraints))
# --- 2️⃣ Constrain using a specific Vertex on the circle edge
# Get a point ~50% around the circle
position = circle_edge.positionAt(0.5)
vertex = cq.Vertex.makeVertex(*position.toTuple())

try:
    assy.constrain("circle", vertex, "green_box", box.val(), "Point")
except KeyError as exc:
    pass

# --- 3️⃣ Constrain with a distance offset (param)
# This keeps blue_box at least 5 units away from green_box's center
try:
    assy.constrain("green_box", "blue_box", "Point", param=5)
except KeyError as exc:
    pass

# Solve the assembly
assy.solve()

# Show the result
# show_object(assy)
