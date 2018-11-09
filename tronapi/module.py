
class Module:
    def __init__(self, tron):
        self.tron = tron

    @classmethod
    def attach(cls, target, module_name=None):
        if module_name is not None:
            module_name = cls.__name__.lower()

        if hasattr(target, module_name):
            raise AttributeError(
                "Cannot set {0} module named '{1}'.  The Tron object "
                "already has an attribute with that name".format(
                    target,
                    module_name,
                )
            )

        tron = target
        if isinstance(target, Module):
            tron = target.tron

        setattr(target, module_name, cls(tron))
