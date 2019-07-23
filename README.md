# Medieval-Itineraries
A collection of late-medieval itineraries - Bishops, Kings, Travelers

This project is part of the work of the "Travelers Lab" - a medieval history research 
group based at Wesleyan University.

NOTE: Currently the system of itineraries and gazetteers is based on lists of tabular
data (csv's) with pieces of code to move between them.  Eventually, large portions of
the data could (should...) be modified to function as a relational database, but currently, 
for ease of use in instructional settings, we are maintaining the various pieces of data
as independent csv's that can be accessed easily by students for visualization, 
research, and other projects.

website: http://travelerslab.research.wesleyan.edu

# Note on Encoding
All of the files here are encoded using UTF-8.  If you are adding data or looking for
matches in a gazetteer, it will all work better if your own files are also encoded in
UTF-8.  Downloading a CSV from a google spreadsheet saves a UTF-8 file, but saving a CSV 
from Microsoft Excel does not.  If you are using Excel, you can either copy and paste
your data into google to save as a CSV, or open your excel file in OpenOffice Calc and
when you select "save as" in Calc, there will be a CSV option and an encoding option 
for UTF-8.  You can read about the many tribulations in this question at length here:

https://stackoverflow.com/questions/4221176/excel-to-csv-with-utf8-encoding

# Dependencies
* Python 3.6
* Pandas 0.24.2
* Levenshtein 0.12.0
* pyproj 2.2.1

The python code also makes use of the 'datetime', 'json', and 'requests' python modules. 


# Contact:

* Adam Franklin-Lyons (code and medieval Mediterranean data): adamfl@marlboro.edu
* Gary Shaw (data and research on projects in the UK): gshaw@wesleyan.edu

See also: http://travelerslab.research.wesleyan.edu/faculty/
