"""
 Title:         Shaper API
 Description:   API for shaping sample-esque geometries
 Author:        Janzen Choi

"""

# Libraries
import math, time, os, csv, re
import sm_cubit.visuals.imager as imager
import sm_cubit.visuals.importer as importer
import sm_cubit.visuals.improver as improver
import sm_cubit.interface.reader as reader
import sm_cubit.maths.pixel_maths as pixel_maths
import sm_cubit.maths.grain_maths as grain_maths
import sm_cubit.interface.mesher as mesher
import sm_cubit.maths.statistics as statistics

# API Class
class API:

    def __init__(self, title:str="", input_path:str="./data", output_path:str="./results", output_here:bool=False):
        """
        Class to interact with the sampler code
        
        Parameters:
        * `title`:       Title of the output folder
        * `input_path`:  Path to the input folder
        * `output_path`: Path to the output folder
        * `verbose`:     If true, outputs messages for each function call
        * `output_here`: If true, just dumps the output in ths executing directory
        """
        
        # Initialise internal variables
        self.__pixel_grid__ = []
        self.__grain_map__  = {}
        self.__print_index__ = 0
        self.__img_count__  = 1
        self.__step_size__  = None
        self.__thickness__  = None
        
        # Print starting message
        self.__print_index__ = 0
        time_str = time.strftime("%A, %D, %H:%M:%S", time.localtime())
        self.__print__(f"\n  Starting on {time_str}\n", add_index=False)
                
        # Get start time
        self.__start_time__ = time.time()
        time_stamp = time.strftime("%y%m%d%H%M%S", time.localtime(self.__start_time__))
        
        # Define input and output
        self.__input_path__ = input_path
        self.__get_input__  = lambda x : f"{self.__input_path__}/{x}"
        title = "" if title == "" else f"_{title}"
        title = re.sub(r"[^a-zA-Z0-9_]", "", title.replace(" ", "_"))
        self.__output_dir__ = "." if output_here else time_stamp
        self.__output_path__ = "." if output_here else f"{output_path}/{self.__output_dir__}{title}"
        self.__get_output__ = lambda x : f"{self.__output_path__}/{x}"

        # Define paths
        self.__i_path__      = self.__get_output__("input_file.i")
        self.__spn_path__    = self.__get_output__("voxellation.spn")
        self.__exodus_path__ = self.__get_output__("mesh.e")

        # Create directories
        safe_mkdir(output_path)
        safe_mkdir(self.__output_path__)

    def __print__(self, message:str, add_index:bool=True) -> None:
        """
        Displays a message before running the command (for internal use only)
        
        Parameters:
        * `message`:   the message to be displayed
        * `add_index`: if true, adds a number at the start of the message
        """
        if add_index:
            self.__print_index__ += 1
            print(f"   {self.__print_index__})\t", end="")
            message += " ..."
        print(message)

    def __del__(self):
        """
        Prints out the final message (for internal use only)
        """
        time_str = time.strftime("%A, %D, %H:%M:%S", time.localtime())
        duration = round(time.time() - self.__start_time__)
        self.__print__(f"\n  Finished on {time_str} in {duration}s\n", add_index=False)
    
    def read_pixels(self, csv_file:str, step_size:int=1) -> None:
        """
        Reads the sample data from the CSV file
        
        Parameters:
        * `csv_file`:  The CSV file that the data is read from
        * `step_size`: The step size of the sample data uses 
        """
        self.__print__("Reading pixel data from CSV file")
        self.__step_size__ = step_size
        csv_path = self.__get_input__(csv_file)
        self.__pixel_grid__, self.__grain_map__ = reader.read_pixels(csv_path, step_size)

    def read_image(self, image_file:str, ipf:str="x") -> None:
        """
        Reads the sample data from an image; requires the `read_pixels` function
        to be called beforehand
        
        Parameters:
        * `image_file`: The image that the data is read from
        * `ipf`:        The IPF scheme that the data is coloured using
        """
        self.__print__("Importing pixel data from image file")
        new_pixel_grid = importer.convert_image(self.__grain_map__, self.__get_input__(image_file), ipf)
        self.__step_size__ *= len(self.__pixel_grid__)/len(new_pixel_grid)
        self.__pixel_grid__ = new_pixel_grid

    def clean_pixels(self, iterations:int=1) -> None:
        """
        Cleans the pixels
        
        Parameters:
        * `iterations`: The number of iterations that the cleaning is conducted
        """
        self.__print__(f"Cleaning up the pixels for {iterations} iterations")
        for _ in range(iterations):
            self.__pixel_grid__ = improver.clean_pixel_grid(self.__pixel_grid__)

    def smoothen_edges(self, iterations:int=1) -> None:
        """
        Smoothens the grain edges
        
        Parameters:
        * `iterations`: The number of iterations that the cleaning is conducted
        """
        self.__print__(f"Smoothing the grain edges for {iterations} iterations")
        for _ in range(iterations):
            self.__pixel_grid__ = improver.smoothen_edges(self.__pixel_grid__)

    def pad_edges(self, iterations:int=1) -> None:
        """
        Adds padding to the grain edges
        
        Parameters:
        * `iterations`: The number of iterations that the cleaning is conducted
        """
        self.__print__(f"Padding the grain edges for {iterations} iterations")
        for _ in range(iterations):
            self.__pixel_grid__ = improver.pad_edges(self.__pixel_grid__)

    def assimilate(self, threshold:int=5) -> None:
        """
        Forces the small grains to merge with neighbouring, bigger grains
        
        Parameters:
        * `threshold`: The pixel threshold for which grains will be merged
        """
        self.__print__(f"Assimilating grains smaller than {threshold} pixels")
        self.__pixel_grid__ = improver.remove_small_grains(threshold, self.__pixel_grid__)

    def merge_grains(self, threshold:int=10) -> None:
        """
        Combines grains with similar crystal orientations; note that this is
        not the recommended way to merge grains, and should only be used for
        experimenting / testing purposes
        
        Parameters:
        * `threshold`: The square difference threshold for which grains will be merged
        """
        self.__print__(f"Merging grains with orientation differences less than {threshold}")
        self.__pixel_grid__ = improver.merge_grains(self.__pixel_grid__, self.__grain_map__, threshold)

    def rotate_CW_90(self, iterations:int) -> None:
        """
        Rotates the pixels clockwise by 90 degrees
        
        Parameters:
        * `iterations`: The number of iterations that the cleaning is conducted
        """
        self.__print__(f"Rotating the pixels CW 90 degrees {iterations} times")
        self.__pixel_grid__ = list(zip(*self.__pixel_grid__[::-1])) # no idea how
    
    def vertical_flip(self) -> None:
        """
        Vertically flips the pixels
        """
        self.__print__("Vertically flips the pixels")
        self.__pixel_grid__ = self.__pixel_grid__[::-1]

    def redefine_domain(self, x_min:float, x_max:float, y_min:float, y_max:float) -> None:
        """
        Redefines the domain
        
        Parameters:
        * `x_min`: The lowest x value for the new domain
        * `x_max`: The highest x value for the new domain
        * `y_min`: The lowest y value for the new domain
        * `y_max`: The highest y value for the new domain
        """
        self.__print__("Redefining the domain")
        
        # Get boundaries
        x_min = round(x_min / self.__step_size__)
        x_max = round(x_max / self.__step_size__)
        y_min = round(y_min / self.__step_size__)
        y_max = round(y_max / self.__step_size__)

        # Get new and original lengths
        x_size = len(self.__pixel_grid__[0])
        y_size = len(self.__pixel_grid__)
        new_x_size = x_max - x_min
        new_y_size = y_max - y_min

        # Create new pixel grid and replace
        new_pixel_grid = pixel_maths.get_void_pixel_grid(new_x_size, new_y_size)
        for row in range(y_size):
            for col in range(x_size):
                new_col, new_row = abs(col-x_min), abs(row-y_min)
                if new_col >= 0 and new_row >= 0 and new_col < new_x_size and new_row < new_y_size:
                    new_pixel_grid[new_row][new_col] = self.__pixel_grid__[row][col]
        self.__pixel_grid__ = new_pixel_grid

    def decrease_resolution(self, factor:int) -> None:
        """
        Decreases the resolution of the voxellation
        
        Parameters:
        * `factor`: The factor of the resolution decrease
        """
        self.__print__("Decreasing the sample resolution")
        self.__step_size__ *= factor
        new_x_size = math.ceil(len(self.__pixel_grid__[0]) / factor)
        new_y_size = math.ceil(len(self.__pixel_grid__) / factor)
        new_pixel_grid = pixel_maths.get_void_pixel_grid(new_x_size, new_y_size)
        for row in range(new_y_size):
            for col in range(new_x_size):
                new_pixel_grid[row][col] = self.__pixel_grid__[row * factor][col * factor]
        self.__pixel_grid__ = new_pixel_grid

    def increase_resolution(self, factor:int) -> None:
        """
        Increases the resolution of the voxellation
        
        Parameters:
        * `factor`: The factor of the resolution increases
        """
        self.__print__("Increasing the sample resolution")
        self.__step_size__ /= factor
        new_x_size = len(self.__pixel_grid__[0]) * factor
        new_y_size = len(self.__pixel_grid__) * factor
        new_pixel_grid = pixel_maths.get_void_pixel_grid(new_x_size, new_y_size)
        for row in range(new_y_size):
            for col in range(new_x_size):
                new_pixel_grid[row][col] = self.__pixel_grid__[math.floor(row / factor)][math.floor(col / factor)]
        self.__pixel_grid__ = new_pixel_grid

    def cut_circle(self, x_centre:float, y_centre:float, radius:float) -> None:
        """
        Creates a circular cut
        
        Parameters:
        * `x_centre`: The x coordinate of the centre of the circle
        * `y_centre`: The y coordinate of the centre of the circle
        * `radius`:   The radius of the circle
        """
        self.__print__("Performing circular cut")
        x_centre = round(x_centre / self.__step_size__)
        y_centre = round(y_centre / self.__step_size__)
        radius = round(radius / self.__step_size__)
        coordinates_list = pixel_maths.get_coordinates_within_circle(x_centre, y_centre, radius)
        self.__pixel_grid__ = pixel_maths.remove_pixels(self.__pixel_grid__, coordinates_list)

    def cut_rectangle(self, x_min:float, x_max:float, y_min:float, y_max:float) -> None:
        """
        Creates a rectangular cut
        
        Parameters:
        * `x_min`: The lowest x value for the rectangular cut
        * `x_max`: The highest x value for the rectangular cut
        * `y_min`: The lowest y value for the rectangular cut
        * `y_max`: The highest y value for the rectangular cut
        """
        self.__print__("Performing rectangular cut")
        x_min = round(x_min / self.__step_size__)
        x_max = round(x_max / self.__step_size__)
        y_min = round(y_min / self.__step_size__)
        y_max = round(y_max / self.__step_size__)
        coordinates_list = pixel_maths.get_coordinates_within_rectangle(x_min, x_max, y_min, y_max)
        self.__pixel_grid__ = pixel_maths.remove_pixels(self.__pixel_grid__, coordinates_list)

    def cut_triangle(self, x_a:float, y_a:float, x_b:float, y_b:float, x_c:float, y_c:float) -> None:
        """
        Creates a triangular cut; sloped cuts may not be very clean
        
        Parameters:
        * `x_a`: The x coordinate of the first corner of the triangle
        * `y_a`: The y coordinate of the first corner of the triangle
        * `x_b`: The x coordinate of the second corner of the triangle
        * `y_b`: The y coordinate of the second corner of the triangle
        * `x_c`: The x coordinate of the third corner of the triangle
        * `y_c`: The y coordinate of the third corner of the triangle
        """
        self.__print__("Performing triangular cut")
        x_a = round(x_a / self.__step_size__)
        y_a = round(y_a / self.__step_size__)
        x_b = round(x_b / self.__step_size__)
        y_b = round(y_b / self.__step_size__)
        x_c = round(x_c / self.__step_size__)
        y_c = round(y_c / self.__step_size__)
        coordinates_list = pixel_maths.get_coordinates_within_triangle(x_a, y_a, x_b, y_b, x_c, y_c)
        self.__pixel_grid__ = pixel_maths.remove_pixels(self.__pixel_grid__, coordinates_list)

    def cut_mask(self, png_file:str) -> None:
        """
        Creates a custom cut by reading from a file; the 'void' is specified by black pixels
        
        Parameters:
        * `png_file`: The file containing an image of the custom cut
        """
        self.__print__("Performing cut using a mask")
        coordinates_list = imager.get_void_pixels(self.__get_input__(png_file))
        self.__pixel_grid__ = pixel_maths.remove_pixels(self.__pixel_grid__, coordinates_list)

    def add_homogenised(self) -> None:
        """
        Replaces the void with homogenised grain with average orientation weighted by area;
        note that this adds the homogenised (i.e., average) orientations to the end of the
        orientation file, if exported
        """
        self.__print__("Replacing void with average grain")

        # Adds average orientation as new grain
        avg_ori = grain_maths.get_average_orientation(self.__grain_map__)
        self.__grain_map__[pixel_maths.HOMOGENOUS_PIXEL_ID] = grain_maths.get_grain_dict(0, *avg_ori, 0)

        # Replaces void with homogenised grain
        for row in range(len(self.__pixel_grid__)):
            for col in range(len(self.__pixel_grid__[0])):
                if self.__pixel_grid__[row][col] == pixel_maths.VOID_PIXEL_ID:
                    self.__pixel_grid__[row][col] = pixel_maths.HOMOGENOUS_PIXEL_ID

    def visualise(self, png_file:str="image", ipf:str=None) -> None:
        """
        Creates an image of the sample
        
        Parameters:
        * `png_file`: The file of the image
        * `ipf`:      The IPF scheme that the image uses for colouring the grain orientations
        """
        self.__print__("Visualising the sample")
        imager.generate_image(self.__pixel_grid__, self.__grain_map__, self.__get_output__(f"{png_file}_{self.__img_count__}"), ipf)
        self.__img_count__ += 1
        
    def mesh(self, psculpt_path:str, thickness:float, adaptive:bool=False) -> None:
        """
        Generates a mesh and exports the orientations
        
        Parameters:
        * `psculpt_path`: The path to PSculpt
        * `thickness`:    The thickness of the mesh - the thickness should be a multiple of the step size
        * `adaptive`:     Whether to turn on the adaptive meshing capabilities of PSculpt
        """
        self.__print__("Meshing the sample")
        
        # Remapping the grains
        self.__pixel_grid__, self.__grain_map__ = reader.remap_grains(self.__pixel_grid__, self.__grain_map__)
        
        # Conduct mesh
        if thickness < self.__step_size__:
            raise ValueError(f"The specified thickness must be at least {self.__step_size__}")
        self.__thickness__ = round(thickness / self.__step_size__)
        has_void = pixel_maths.VOID_PIXEL_ID in [pixel for pixel_list in self.__pixel_grid__ for pixel in pixel_list]
        mesher.coarse_mesh(psculpt_path, self.__step_size__, self.__i_path__, self.__spn_path__, self.__exodus_path__, self.__pixel_grid__, self.__thickness__, has_void, adaptive)

    # Exports statistics
    def export_statistics(self, file_name:str="input_orientations", orientation:bool=False, area:bool=False, phase:bool=False) -> None:
        """
        Exports the statistics of the mesh
        
        Parameters:
        * `file_name`:   The name of the file
        * `orientation`: Whether to export the orientations of the grains
        * `area`:        Whether to export the areas of the grains
        * `phase`:       Whether to export the phase of the grains
        """
        self.__print__("Exporting the statistics")

        # Define statistics to extract
        statistics_list = []
        statistics_list += ["phi_1", "Phi", "phi_2"] if orientation else []
        statistics_list += ["size"] if area else []
        statistics_list += ["phase_id"] if phase else []

        # Print progress
        statistics_string = ", ".join(statistics_list) if statistics_list != [] else "nothing"
        self.__print__(f"Exporting {statistics_string}")
        
        # Extract statistics
        spn_size = [self.__thickness__, len(self.__pixel_grid__), len(self.__pixel_grid__[0])]
        has_void = pixel_maths.VOID_PIXEL_ID in [pixel for pixel_list in self.__pixel_grid__ for pixel in pixel_list]
        extracted_statistics = statistics.get_stastistics(self.__exodus_path__, self.__spn_path__, spn_size, self.__grain_map__, has_void, statistics_list)
        file_path = self.__get_output__(f"{file_name}.csv")
        
        # Writes the data to the CSV file
        with open(file_path, "w+") as file:
            writer = csv.writer(file)
            for row in extracted_statistics:
                writer.writerow(row)

    def export_dimensions(self, file_name:str="dim.txt") -> None:
        """
        Exports the SPN dimensions
        
        Parameters:
        * `file_name`:   The name of the file
        """
        self.__print__("Exporting the dimensions of the SPN file")
        file_path = self.__get_output__(file_name)
        with open(file_path, "w+") as file:
            if hasattr(self, "thickness"):
                file.write(f"x = {self.__thickness__ * self.__step_size__}\n")
            file.write(f"y = {len(self.__pixel_grid__) * self.__step_size__}\n")
            file.write(f"z = {len(self.__pixel_grid__[0]) * self.__step_size__}\n")

def safe_mkdir(dir_path:str) -> None:
    """
    Creates a directory only if it does not exist
    
    Parameters:
    * `dir_path`: The path in which the directory will be created
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
