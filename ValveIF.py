import time

class ValveIF:

    def __init__(self, valves , valves_fault, valves_mainMux): 
        self.valves=valves
        self.valves_fault=valves_fault
        self.valves_mainMux=valves_mainMux

    def show_source(self, source_index):
        self.source_index=source_index
        self.stop_all()
        time.sleep(0.3)#probabilmente da ridurre
        self.valves_mainMux[source_index].set_property("drop", False)
    
    def valveFault(self, index):
        self.valves_fault[index].set_property("drop", True)
        self.valves[index].set_property("drop", False)

    def valveWorking(self, index):
        self.valves_fault[index].set_property("drop", True)
        self.valves[index].set_property("drop", False)

    def stop_all(self):
        for valve in self.valves_mainMux:
            valve.set_property("drop", True)