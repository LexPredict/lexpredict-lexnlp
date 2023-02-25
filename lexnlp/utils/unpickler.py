import pickle


class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        renamed_module = module
        if module == "sklearn.tree.tree":
            renamed_module = "sklearn.tree"
        if module == "sklearn.ensemble.forest":
            renamed_module = "sklearn.ensemble._forest"
        return super(RenameUnpickler, self).find_class(renamed_module, name)


def renamed_load(file_obj):
    return RenameUnpickler(file_obj).load()
