

class DeepWell:

    def __init__(self, well_id, gpm, total):
        self.well_id = well_id
        self.gpm = gpm
        self.total = total
    
    def get_gpm(self):
       return self.gpm
   
    def get_total(self):
        return self.total
    
    def update(self, gpm, total):
        self.gpm = gpm
        self.total = total