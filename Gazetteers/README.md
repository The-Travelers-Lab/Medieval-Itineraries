# Initial Note:

If you would like to work on any of these items, please contact either Adam
Franklin-Lyons (adamfl@marlboro.edu) or Gary Shaw (gshaw@wesleyan.edu) for 
more detailed instructions.  If you are working on an Itinerary and have produced
new locations that can be added to the full Gazetteer, either branch the existing 
gazetteer or, alternately, upload your csv files to the "New Gazetteer Data" folder 
for re-checking prior to addition to the full dataset.  For instructions on 
accessing the Gazetteer for work on a new itinerary, see the README instructions 
in the Itinerary-Project-Code folder (or contact one of us with questions.)

# A Note about geo_id codes

When possible, the geo_id column in all gazetteers is taken from geonames.org,
a large set of linked open data with unique id numbers for every geographic
location.  All geo_id entries that are numeric and have no alphabetical characters 
are from the geonames dataset.  Any geo_id with alphabetical characters comes in
one of three different types:

TL_#### - TL for "Travelers Lab" - these are either obscure or historical locations
  that we have often researched, although sometime we still do not know where they 
  are (if the "checked" column has an "R" in it, we really don't have a good idea and
  if you want, you can look in to those entries and see what you find.  Let us know!)
  The specific id numbers were generated randomly by the lab for our itineraries.
GNA_#### - These are a subset of the above locations, except that their existence
  and specific location is not in doubt and can easily be seen in online maps (many
  of these locations appear obviously labelled in google maps, for instance).  They
  simply have not been entered in geonames yet.  Geonames allows for new location 
  submissions, so if you are feeling enterprising, add some locations to geonames,
  get the new geonames location code, and replace the previous GNA id (but do let us
  know that will be happening.)
<ItCode>_## - These are a mix of different codes each starting with the specific
  itinerary id followed by only a two digit number.  They represent places that are
  not strictly speaking "real" but that are geographically relevant.  The main 
  examples include locations like "On the Ebro River" or "On ship between Mallorca
  and Barcelona."  The location was made up to fit the rough geographic guidelines
  provided by the sources (and as such will never be part of geonames) and the 
  location is usually used only in a single itinerary collection, so it receives an 
  id number based on the itinerary code for that specific itinerary dataset.

# To Do List:

## Episcopal Travel Gazetteer
* Begin Compilation...
