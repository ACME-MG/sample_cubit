"""
 Title:         Grain
 Description:   Represents a grain
 Author:        Janzen Choi

"""

# Grain class
class Grain:
    
    def __init__(self, phi_1:float, Phi:float, phi_2:float, size:int, phase_id:int):
        """
        Contains information about a grain
        
        Parameters:
        * `phi_1`:    The average phi_1 orientation of the grain
        * `Phi`:      The average Phi orientation of the grain
        * `phi_2`:    The average phi_2 orientation of the grain
        * `size`:     The number of pixels in the grain
        * `phase_id`: The phase ID of the grain
        """
        self.phi_1    = phi_1
        self.Phi      = Phi
        self.phi_2    = phi_2
        self.size     = size
        self.phase_id = phase_id
    
    def get_orientation(self) -> tuple:
        """
        Returns the orientation of the grain
        """
        return self.phi_1, self.Phi, self.phi_2

    def increment_size(self) -> None:
        """
        Increments the total number of pixels in the grain
        """
        self.size += 1
    
    def get_size(self) -> int:
        """
        Returns the size of the grain
        """
        return self.size
    
    def get_phase_id(self) -> int:
        """
        Returns the phase id
        """
        return self.phase_id

    def get_all_stats(self) -> list:
        """
        Returns a listed summary of the statistics
        """
        return [self.phi_1, self.Phi, self.phi_2, self.size, self.phase_id]
