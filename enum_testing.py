from src.enum_helpers import create_str_enum, extend_str_enum

Enum1 = create_str_enum("Enum1", ["member 1", "member 2"])
print("Enum1 members:")
print("\n".join((f"{member.name}: {member.value}" for member in Enum1)))

Enum2 = create_str_enum("Enum2", ["member 3", "member 4"])
print("\nEnum2 members:")
print("\n".join((f"{member.name}: {member.value}" for member in Enum2)))

Enum3 = extend_str_enum(Enum1, Enum2)
print("\nEnum3 members:")
print("\n".join((f"{member.name}: {member.value}" for member in Enum3)))

new_members = {"MEMBER5": "member 5", "MEMBER6": "member 6"}
Enum4 = extend_str_enum(Enum3, new_members)
print("\nEnum4 members:")
print("\n".join((f"{member.name}: {member.value}" for member in Enum4)))

new_members = ["member 7", "member 8"]
Enum5 = extend_str_enum(Enum4, new_members)
print("\nEnum5 members:")
print("\n".join((f"{member.name}: {member.value}" for member in Enum5)))
