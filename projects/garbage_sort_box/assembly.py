import cadquery as cq
from helpers.abstracts import AssemblerABC
from projects.garbage_sort_box.parts import PartType, Builder


class Assembler(AssemblerABC):
    PartTypeEnum = PartType
    BuilderClass = Builder

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        width: int | float,
        depth: int | float,
        height: int | float,
        material_thickness: int | float,
        visual_offset: int = 0,
    ):
        super().__init__(width, depth, height, material_thickness)
        self.visual_offset = visual_offset

    @property
    def x_offset(self):
        return ((self._x_length - self._material_thickness) / 2) + self.visual_offset

    @property
    def y_offset(self):
        return ((self._y_length - self._material_thickness) / 2) + self.visual_offset

    @property
    def z_offset(self):
        return self._z_length / 2

    @property
    def metadata_map(self) -> dict[PartType, dict]:
        # pylint: disable=no-value-for-parameter
        return {
            PartType.BOTTOM: {
                "loc": cq.Location(cq.Vector(0, 0, 0)),
                "name": "Bottom Panel",
                "color": cq.Color("burlywood"),
            },
            PartType.LONG_SIDE: {
                "loc": cq.Location(cq.Vector(0, self.y_offset, self.z_offset)),
                "name": "Long side panel",
                "color": cq.Color("burlywood2"),
            },
            PartType.LONG_SIDE_INVERSE: {
                "loc": cq.Location(cq.Vector(0, -self.y_offset, self.z_offset)),
                "name": "Long side panel inverse",
                "color": cq.Color("burlywood2"),
            },
            PartType.SHORT_SIDE: {
                "loc": cq.Location(cq.Vector(self.x_offset, 0, self.z_offset)),
                "name": "Short side panel",
                "color": cq.Color("burlywood4"),
            },
            PartType.SHORT_SIDE_INVERSE: {
                "loc": cq.Location(cq.Vector(-self.x_offset, 0, self.z_offset)),
                "name": "Short side panel inverse",
                "color": cq.Color("burlywood4"),
            },
        }
