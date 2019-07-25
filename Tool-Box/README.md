# Description:

This folder contains detailed instructions for moving from a published
itinerary or set of sources to a final itinerary that can be analyzed 
with the tools presented here.

# Contents:
* Basic-Instructions
* Flow Chart for location checking

# Python:

If you want to use python, the code in this section depends on pandas, 
so the easiest installation will be to get the Anacondas package, which
is designed for data science tasks and includes pandas and other 
nice visualization libraries:

https://www.anaconda.com/distribution/

The other dependencies you will have to include manually.  After 
installing anaconda, open your terminal or command prompt (Terminal on 
a mac, command prompt in windows), and enter the following line:

conda install -c conda-forge python-levenshtein

Then open the Anaconda Navigator (installed with anaconda) and check that
the Levenshtein package has appeared.  Click on "Environments" and look 
at the installed packages in the "root" environment.  There should be a
package installed called "python-levenshtein" (you can use the search box 
in the upper right to find it.)  While you are there, choose the list of
not installed packages, search for "pyproj" and install that package as 
well.  Both these steps will take a bit of time for the computer to 
install, but when they are finished you are ready to go.
