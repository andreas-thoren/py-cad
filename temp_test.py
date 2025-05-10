class Base:
    _my_attr = ["Base"]
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        print(f"Init_subclass: {cls.__name__}")
        parent_my_attr = getattr(super(cls, cls), "_my_attr")
        print(parent_my_attr)
        cls._my_attr = parent_my_attr + cls._my_attr

class Mid2(Base):
    _my_attr = ["Mid2"]

class Mid3(Base):
    _my_attr = ["Mid3"]

class Mid(Base):
    _my_attr = ["Mid"]

class Leaf(Mid2, Mid, Mid3):
    _my_attr = ["Leaf"]
    pass

leaf = Leaf()
print(leaf._my_attr)
