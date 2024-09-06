
#self.nvvidconv_2.set_property("flip-method", self.flip_method)


class TilerIF:
    def __init__(self, pipeline, name,):
        self.name = name
        self.pipeline = pipeline
        self.vidconv = self.pipeline.get_by_name(self.name)
        if not self.vidconv:
            print(f"Unable to get {self.name}")

    #TBD