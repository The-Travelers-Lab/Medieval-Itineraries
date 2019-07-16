"""
-*- coding: utf-8 -*-

gazetteer_class.py

A class meant to wrap up several functions for organizing and searching a
gazetteer of place names generated for medieval travel and locations.
The class based on a Pandas dataframe, reading in a csv to the class and
exporting the modified data back to a new csv.

The class also uses a secondary class called "geonames_lookup" that creates
url's to call data from geonames.org.  The basic search used in the gazetteer
looks up a place name by the nearest available geometry - it requires latitude
and longitude as inputs and returns a dictionary with a name, distance, geoid,
and other attributes.  The gazetteer processes only those first three,
dropping the other attributes after lookup.  The name_lookup will not run
unless the proper columns are present.

The program also outputs the index name or number for all online searches
executed.  The creation of the class only needs to set monitor to False to
turn this off, but it helps me know where in a long list of url searches
the program is.

    Variable List:
        self.gaz_df - The Pandas DataFrame read-in version of the Gazetteer
            file entered for the instantiation of your object.
        self.name - A default output file name based on the input file name.
        self.count - Starts at 0 - this variable tracks the row index of the
            row in use for the geonames URL lookup.
        self.monitor - True/False - whether to print out the self.count index
            tracker during the online search for geonames id numbers.
        self.user_name - the geonames username of the user.  This must be a
            valid geonames username or the URL lookup will fail.
            see: http://www.geonames.org/export/web-services.html
        self.empty - tracks which cells in the geoid column are filled in or
            not to prevent duplicate searches of already discovered matches.

    Function List:
        csv_output(self, out_file_name, name_lookup=False) - requires a file
            name where it prints the gaz_df DataFrame.  The function can
            optionally be instructed to do a name search in the geonames.org
            database; 'double' does the first name search and then a broader
            version of the same search for any geographic name, not just
            populated places.
        check_existing_gaz(self, existing_gaz_file, save=False,
                           merge=False, drop_matches=True, merge_file=None):
            Takes two Gazetteers, one self and a second, and does a full
            geoid check on both if necessary.  Then it creates a new column
            in self where the geoid's match.  If the names are substantially
            similar, a reference column registers True, whereas if they are
            substantially different, the name will appear in a new
            reference_name column, but the True/False match column will still
            rregister false.  If save and merge are set to True, the function
            will output a single unified gazetteer with exact matches dropped
            as duplicates and possible matches unified with a similar_names
            column for checking.  The output includes a summary txt file.
        itinerary_labels(self, itin_df, itin_code, match='modern_name'):
            Takes a given itinerary, goes through the Gazetteer, and adds the
            entered itinerary code to the itin_list column.  If the column
            does not exist it creates the column, and if there are already
            entries, it adds new labels separated by semi-colons.  Blank
            entries are filled with the new code; entries not found print a
            message with the missing name.
        geoname_id_lookup(self, number='single'):
            Runs every row of the gazetteer dataframe through an online lookup
            for matching lat_long coordinates (_geoname_search).  All hits are
            then run through a name match (_name_match) - all names
            registering over 70% similarity to the 'modern_name' column have
            their geoids filled in automatically.  Those with a weaker match
            create new columns with the name and geoid listed as a 'guess' to
            be checked manually.  Changing number to 'double' will provide
            a second, more general, guess in a second set of guess columns
            with possible names, geoids, and distances.  These do not run
            a string similarity test, but only fill in the guesses.
        error_output(self, tofile=False, filename=None):
            Prints out the lists of errors generated by other columns,
            including line by line errors such as when geonames returns a
            lookup error.  If tofile remains False, the errors are printed
            out in interactive python, otherwise a txt file is generated.

    Internal Functions:
        _match_gaz_lines(self, ref_gaz_df, gaz_row):
            Takes the geoid of a gazetteer row and searches for a similar
            match in a reference gazetteer.  If the geoids match, the function
            tests the modern_name similarity as well.
        _merge_dataframes(self, merge_gaz, file_name, drop_matches=True):
            Takes the self dataframe and merges it with a previous gazetteer.
            Making drop_matches False will leave all rows, simply
            concatenating the two frames.  Leaving it True will unify all
            geoid matches with similar names.
        _ping(self):
            Sends a single search to geonames to check if there is internet
            and if the geonames website is available.  Failed searches
            prevent the program from running any further lookups.
        _geoname_search(self, row, feature='P'):
            Takes one line of a gazetteer dataframe, sending the lat/long
            coordinates to geonames and returning the most likely populated
            place.
        _geoname_error_test(self, url_return):
            Checks if the returned json data from geonames contains any error
            warnings.  In particular, this will print out the messages of
            particular error codes such as invalid usernames or insufficient
            lookup tokens (max tends to be around 250 per hour).
        _name_match(self, geo_row, ref_item, ref_key=None):
            This function takes a reference name and compares it to the
            'modern_name' in a Gazetteer row.  If they are 70% similar
            according to a Levenshtein similarity test, the function returns
            True, otherwise it returns False.  This function allows "ref_name"
            to either be a string used for matching or a column reference in
            the geo_row both compared directly with the 'modern_names'.  To
            call a column reference, enter the column name as the ref_key.
        _reorganize_cols(self, num):
            Creates new columns at the end of the dataframe containing the
            geonames lookup guesses by attribute rather than the single
            dictionary item returned by the geonames lookup itself.  The
            function labels them either first or second guess according to
            the 'num' variable.
        _dict_get(self, dict_item, key):
            Returns the dictionary item at the given key.  If the dict_item is
            not a dictionary or the key does not exist, it returns None.
        _verify_all(self):
            runs both of the following verifies and allows other functions
            to run or not depending on successful results.
        _verify_columns(self) - only checks to make sure that the gazetteer
            has properly labelled columns for the other functions to work
            correctly (modern_name, latitude, and longitude).
        _verify_lat_long(self) - only checks that there are no obvious out of
            bounds mistakes in the coordinates (beyond 90 or 180).

@author: Adam Franklin-Lyons
    Marlboro College | Python 3.7

Created on Tue May 21 20:27:31 2019
"""

import pandas as pd
from geonames_lookup_class import Geonames
import Levenshtein as lev
from requests.exceptions import ConnectionError

class Gazetteer:

    def __init__(self, gaz_file, geoname_username, monitor=True):
        """
        Import a gazetteer file into a Pandas DataFrame.
        This also requires a Geonames ID for lookup purposes - without a
        valid name, the geonames lookup feature will not function.
        """
        self.gaz_df = pd.read_csv(gaz_file, error_bad_lines=False)
        self.name = gaz_file.split('.')[0]
        self.count = 0
        self.monitor = monitor
        self.user_name = geoname_username
        self.error_checks = []
        self.all_good = self._verify_all()
        if 'geoid' in self.gaz_df.columns.tolist():
            self.empty = self.gaz_df[self.gaz_df['geoid'].isna()].index
        else: self.empty = self.gaz_df.index

    def csv_output(self, out_file_name=None, name_lookup=False):
        """
        Prints the data to a csv - this can run all other functions
        directly by calling 'name_lookup' which either can be True for
        a simple lookup or 'double' to do the spot search as well.
        """
        if name_lookup:
            outcome = self.geoname_id_lookup(name_lookup)
            print(outcome)
        if out_file_name==None:
            out_file_name = (self.name + '_processed.csv')
        self.gaz_df.to_csv(out_file_name, index=False)

    def check_existing_gaz(self, existing_gaz_file, save=False,
                           merge=False, drop_matches=True, merge_file=None):
        """
        Takes two Gazetteers, one self and a second, and does a full geoid
        check on both if necessary.  Then it creates new columns in self
        where the geoid's match.  If the names are substantially similar,
        a third column registers True, whereas if the are substantially
        different, the name will appear in the existing name column, but
        the True/False match column will still register false.

        NOTE: if merge is set to True, the output of the function becomes two
        variables - a Gazetteer Dataframe and the summary message.  With merge
        as False, only the summary message is output.
        """
        message = ['Results of the Existing Gazeteer match process:']
        exist_gaz = Gazetteer(existing_gaz_file, self.user_name)
        gaz_list = [self, exist_gaz]

        # Checks if both Gazetteers contain correct columns and geoids
        for gaz in gaz_list:
            if not gaz.all_good:
                print('please fix the {} Gazetteer errors before '
                         'proceeding.'.format(gaz.name))
                return None
            if ('geoid' not in gaz.gaz_df.columns or
                gaz.gaz_df.geoid.dropna().empty):
                check = gaz.geoname_id_lookup()
                if check=='Failure!':
                    gaz.error_output(tofile=True)
                    print('There were errors - check output file.')
                    return None
        # Reorganizes exact matches and partial matches into columns in self
        zipped_matches = zip(*self.gaz_df.apply(lambda x:
                    self._match_gaz_lines(exist_gaz.gaz_df, x), axis=1))
        self.gaz_df['match'], self.gaz_df['exist_name'] = zipped_matches
        matches = self.gaz_df[self.gaz_df['match']].index
        found_names = self.gaz_df[self.gaz_df['exist_name'].notna()].index
        dif_names = found_names.difference(matches)
        message.append('The following rows have matching geoids and very '
                       'similar names: \n {}'.format((matches + 2).tolist()))
        if dif_names.any():
            message.append('The following rows have matching geoids, but '
                    'different names: \n {}'.format((dif_names + 2).tolist()))
        self.error_checks += message

        # Prints one or both of the dataframes to csv's.
        if save:
            self.csv_output()
            if save=='both':
                exist_gaz.csv_output()
        if merge:
            self._merge_dataframes(exist_gaz, merge_file, drop_matches)
        return None

    def _match_gaz_lines(self, ref_gaz_df, gaz_row):
        """
        compares a gazetteer row with an existing gazetteer by matching the
        geoid column.  If there is an id match, the function checks the names
        in each row for a 70% similarity.  Poorly matching names still get
        recorded in the match column, but with a "False" in the hit column
        to allow for easy filtering between the two, especially during a
        possible merge.
        """
        hit = False
        name = ref_gaz_df.loc[ref_gaz_df.geoid==gaz_row.geoid, 'modern_name']
        if not name.empty:
            name = name.values[0]
            # The _name_match function returns True for a %70 similarity
            hit = self._name_match(gaz_row, name)
        else:
            name = None
        return hit, name

    def _merge_dataframes(self, merge_gaz, file_name, drop_matches=True):
        """
        Takes the self dataframe, removes all rows with identical geoids and
        modern_names and then merges the self dataframe onto the bottom of the
        existing gazetteer dataframe used to check the names and ids.  If you
        have run a double check, theoretically those rows with guesses filled
        in will not be dropped because they will lack a geoid.  However, if
        there is other information in other columns of the matching rows,
        that information will be erased unless "drop_matches" is set to False.
        With drop_matches set to false,
        The output uses a default file_name (unless a new name is provided)
        and prints a csv.
        """
        if drop_matches:
            # Removes exact matches before merging.
            mask_match = self.gaz_df[self.gaz_df['exist_name']==self.gaz_df[
                                                    'modern_name']].index
            # Creates a mask of matching geoids with different names.
            mask_new = self.gaz_df[self.gaz_df['exist_name'].notna()
                                                ].index.difference(mask_match)
            new_frame = self.gaz_df.loc[mask_new, ['geoid', 'modern_name']]
            merge_gaz.gaz_df = pd.merge(merge_gaz.gaz_df, new_frame,
                                    how='outer', on='geoid',
                                    right_index=True, suffixes=('', '_new'))
            # Drops the exact matches from the self df before concatenating.
            self.gaz_df.drop(mask_match.union(mask_new), inplace=True)
        output_gaz = pd.concat([merge_gaz.gaz_df, self.gaz_df], sort=False
                               ).reset_index(drop=True)
        output_gaz.drop(columns=['exist_name','match'], inplace=True)
        if not file_name:
            file_name = '{}_and_{}__merged.csv'.format(self.name,
                                                      merge_gaz.name)
        output_gaz.to_csv(file_name, index=False)
        return output_gaz

    def itinerary_labels(self, itin_df, itin_code, match='modern_name'):
        """
        Takes a given itinerary, goes through the Gazetteer, and adds the
        itinerary code to the itin_list column.  If the columns does not exist
        it creates the column, and if there are already entries, it adds new
        labels separated by semi-colons.  Blank entries are filled with the
        new code and entries not found print a message with the missing name
        and skip that entry.
        """
        message = ['Running "Itinerary Labels" against entered itinerary:']
        names = itin_df[match].dropna().unique()
        if 'itin_list' not in self.gaz_df.columns:
            self.gaz_df['itin_list'] = None

        # Takes each unique name in the Itinerary for adding to the Gazetteer.
        for name in names:
            try:
                test = self.gaz_df[match]==name
                label = self.gaz_df.loc[test,'itin_list'].values[0]
                # Checks if the Itinerary code already exists prior to adding.
                if itin_code in label:
                    None
                else:
                    new_label = label + "; " + itin_code
                    self.gaz_df.loc[test,'itin_list'] = new_label
            except IndexError:
                message.append('{} not found in Gazetteer'.format(name))
            except TypeError:
                # This should return a TypeError when the value is None
                # meaning the cell had no previous codes to append to.
                self.gaz_df.loc[test,'itin_list'] = itin_code
        self.error_checks += message

    def geoname_id_lookup(self, number='single'):
        """
        Runs every row of the gazetteer dataframe through an online lookup for
        matching lat_long coordinates (_geoname_search).  All hits are then
        run through a name match (_name_match) - all names registering over
        70% similarity to the 'modern_name' column have their geoids filled
        in automatically.  Those with a weaker match create new columns with
        the name and geoid listed as a 'guess' to be checked manually.

        Running the function with number='double' will do two versions of the
        search and create 2 guess columns.  The second search removes the
        'populated place' designation used to limit the first search and
        returns only the closest match of any kind.  Matches with a greater
        than %70 similarity from the first attempt will not re-run the
        online lookup in the second attempt.

        Note: Every row lookup does an error check to see if geonames returned
        useable data. If there is an internet problem or a systemic failure
        to look up useable data, the function will return a warning about the
        failure along with messages generated by its helper functions.
        (see: _ping and _geoname_error_test)
        """
        # First run a function that checks the internet and runs a dummy
        # example through the geonames website.
        ping = self._ping()
        if self.all_good and ping:
            # Checks all rows of the dataframe in Geonames 'Populated Places.'
            self.gaz_df['geonames_find'] = self.gaz_df.loc[self.empty].apply(
                            lambda x: self._geoname_search(x, 'P'), axis=1)
            # Checks all returned Geonames data against the existing df name.
            self.gaz_df.loc[self.empty, 'name_match'] = self.gaz_df.loc[
                                self.empty].apply(lambda x: self._name_match(
                                x, x.geonames_find, 'name'), axis=1)
            # Auto-enters geoids in hits and puts non-hits into guess columns.
            self._reorganize_cols(1)

            # re-runs the same search on 'Spots' - multiple types of human
            # places.  NOTE: there might be a better way to run this search!
            if number=='double' and self.all_good:
                self.gaz_df['geonames_find'] = self.gaz_df.loc[self.empty
                    ].apply(lambda x: self._geoname_search(x, 'S'), axis=1)
                self._reorganize_cols(2)
            return 'Success!'
        else:
            # Runs when the internet fails or the gazetteer lacks key data.
            print('The geonames lookup failed.')
            return 'Failure!'

    def error_output(self, tofile=False, filename=None):
        """
        Takes the errors gathered together at any point in the use of the
        specific Itinerary and outputs them either as basic print statements
        in an interactive session or prints to a txt file.  For a txt file
        print, enter: 'tofile=True' as an argument.  The default file name
        is the same as the input itinerary with '_errors.txt' added.  For a
        different label, use the argument: filename='desired_name'
        """
        # Cleans out possible duplicates from _verify_all double runs.
        output = pd.unique(self.error_checks).tolist()
        output.append('So many places to visit!')
        if tofile:
            if filename:
                error_file = filename
            else:
                error_file = self.name + '_errors.txt'
            with open(error_file, 'w') as f:
                f.writelines("{}\n".format(line) for line in output)
        else:
            # Prints to the interactive python rather than a text file.
            for line in output:
                print(line)
        return None

    def _ping(self):
        """
        This is a single location lookup that should return the same result
        every time (the North Pole).  Because sometimes the geonames website
        is not available, this checks on a known location before proceeding
        to the entered gazetteer.  If this returns a NoneType (the result
        when the geonames URL fails), it stops the program from proceeding
        to look up all the other names and creating a list of NoneTypes
        which will then crash the "_reoganize_columns" function.
        """
        # Because I needed a static location with no obvious human objects...
        st_claus = pd.Series({'name':'Claus', 'latitude':90, 'longitude':0})
        # So you know...Santa Claus.
        try:
            # Tests the geonames web search and error check with Mr Claus.
            url_test = self._geoname_search(st_claus, None)
            if url_test:
                print('Santa Claus lives at the '
                      '{}...'.format(url_test['name']))
                return True
            else:
                return False
        # Returns when there is no internet connection for the URL to run.
        except ConnectionError:
            print('You have no internet connection - please connect '
                  'before proceeding.')
            return False

    def _geoname_search(self, row, feature='P'):
        """
        This is the actual Geonames lookup.  It calls a geonames lookup class
        that actually creates the url, submits it to geonames.org and returns
        a dictionary created from the geonames JSON file.  The dictionary
        contains keys including 'name' 'distance' 'geonameId' and others.
        Currently the function allows the class to lookup the default
        'short' version, but could grab more information by adding
        verbose='medium' or 'long' to the nearby_place search.
        """
        # Prints the row number as it looks up since the internet can be slow.
        if self.monitor:
            self.count = row.name
            print(self.count)
        # Creates an instance of the Geonames class for creating the URL's.
        # Would this be faster as a "self" variable created at the beginning?
        if self.all_good:
            geoid_lookup = Geonames(self.user_name)
            location = geoid_lookup.lookup_nearby_place(row.latitude,
                                row.longitude, feature_class=feature)
        else:
            location = None
        # Records the most common errors - too many uses, bad username, etc.
        test = self._geoname_error_test(location)
        attempt = 0
        while test:
            if float(location['distance']) < 5:
                return location
            # If the first lookup is too far away, it does a search without
            # the particular restraint to "Populated place."
            location = geoid_lookup.lookup_nearby_place(row.latitude,
                                                            row.longitude)
            test = self._geoname_error_test(location)
            attempt += 1
            if attempt==2:
                message = ['This row failed to look up in Geonames'
                           'correctly: {}'.format(row.name)]
                self.error_checks.append(message)
                return None

    def _geoname_error_test(self, url_return):
        """
        Takes a returned dictionary or None as looked up from geonames.org.
        Error dictionaries are unpacked and either bad usernames or reference
        limites are flagged.  Returns only True/False
        """
        try:
            if 'geonameId' in url_return.keys():
                return True
        except AttributeError:
            message = ['Please see error messages - try again later.']
            self.error_checks += message
            print(message[0])
            return False
        if 'value' in url_return.keys():
            # Values taken from Geonames error codes
            error_types = {18: 'daily', 19: 'hourly', 20: 'weekly'}
            if url_return['value'] in [18,19,20]:
                message = ['You have used up your {} available lookups '
                           'on geonames.org.  Please try again '
                           'later'.format(error_types[url_return['value']])]
                self.all_good = False
            elif url_return['value']==10:
                message = ['Your username is invalid...please check the '
                           'username and try again.']
            else:
                message = ['There is a problem with the geonames website '
                           'right now.\n Please try again shortly.']
            self.error_checks += message
            print(message[0])
            return False
        else:
            message = ['There is a problem with the geonames website '
                           'right now.\n Please try again shortly.']
            self.error_checks += message
            print(message[0])
            return False

    def _name_match(self, geo_row, ref_item, ref_key=None):
        """
        This function takes a reference name and compares it to the
        'modern_name' in a Gazetteer row.  If they are 70% similar
        according to a Levenshtein similarity test, the function returns
        True, otherwise it returns False.  While this is a decent benchmark,
        it does not do well with potentially longer names like "abalate"
        verses "albalate de cinca" which are not similar enough, but might
        still be the same place.

        This function allows "ref_name" to either be a string used for
        matching or a column reference in the geo_row both compared directly
        with the 'modern_names' cell in the geo_row.
        """
        if ref_key:
            try:
                similarity = lev.ratio(geo_row['modern_name'].lower(),
                                ref_item[ref_key].lower())
            except TypeError:
                similarity = 0
        else:
            try:
                similarity = lev.ratio(geo_row['modern_name'].lower(),
                                ref_item.lower())
            except TypeError:
                similarity = 0
        if similarity > 0.7:
            return True
        else:
            return False

    def _reorganize_cols(self, num):
        """
        This function takes apart the list created by the geonames lookup
        and distributes it between several new columns.  The geoid fills in
        that particular column (or creates it if necessary) and the distance
        is similarly filled or created.  The "name" provided by the geonames
        lookup goes into a "guess" column with a number attached depending on
        whether it is the first lookup or the subsequent "spot" lookup.
        """
        # Creates a mask for matched names, already filled names, and fails
        try:
            matches = self.gaz_df[self.gaz_df['name_match'
                                             ]==True].index
            fails = self.empty.difference(matches)
            self.empty = self.empty.intersection(fails)
            # A series of dictionaries from the Geonames lookup function.
            temp_geodf = pd.Series(self.gaz_df.pop('geonames_find'))
        except ValueError:
            print('Not all values looked up correctly...'
                  'Attempting to repeat the process')
            self.geoname_id_lookup()
        if num==1:
            # Places matched geonames names in the 'name_match' column
            self.gaz_df.loc[matches, 'name_match'] = temp_geodf[matches
                    ].apply(lambda x: self._dict_get(x, 'name'))
            # Reverts False cells in 'name_match' to None for next lookup
            self.gaz_df.loc[fails, 'name_match'] = None
            # Creates a distance column for all matched names in km
            self.gaz_df.loc[matches, 'geo_dist'] = temp_geodf[matches
                    ].apply(lambda x: self._dict_get(x, 'distance'))
            # Fills in the geoid column based on matched names
            self.gaz_df.loc[matches, 'geoid'] = temp_geodf[matches
                    ].apply(lambda x: self._dict_get(x, 'geonameId'))
        # The last three create the guess columns for name, id, and distance.
        self.gaz_df['guess{}'.format(num)] = temp_geodf[fails].apply(
                    lambda x: self._dict_get(x, 'name'))
        self.gaz_df['g_dist{}'.format(num)] = temp_geodf[fails].apply(
                    lambda x: self._dict_get(x, 'distance'))
        self.gaz_df['geoid_guess{}'.format(num)] = temp_geodf[fails
                    ].apply(lambda x: self._dict_get(x, 'geonameId'))

    def _dict_get(self, dict_item, key):
        """
        This function takes a dictionary and a key.  If the item is, in fact,
        a dictionary, the function returns the value for the key in the
        dictionary.  If the item is not a dictionary or if the key is not in
        the dictionary, the function returns the value as None.
        """
        try:
            if isinstance(dict_item, dict):
                value = dict_item[key]
            else:
                value = None
        except KeyError:
            value = None
        return value

    def _verify_all(self):
        """
        This function is only a batch run of the other verification
        functions: correct column names present, no Lat/Long out of bounds,
        and making sure the geoid function has not already been run twice.
        """
        no_flag1 = self._verify_columns()
        no_flag2 = self._verify_lat_long()
        flag3 = 'guess2' in self.gaz_df.columns
        if flag3:
            self.error_checks.append('This Gazetteer has already been run '
                                     'and has guesses for geoids entered.')
        if no_flag1 and no_flag2 and not flag3:
            return True
        else:
            return False

    def _verify_columns(self):
        """
        Verify checks to make sure there are column names required by other
        functions.  If latitude ad longitude are present (as required) it
        then checks to make sure there are no obvious numbers out of bounds.
        """
        no_flag = True
        message = ["Column check results for {}:".format(self.name)]
        columns = self.gaz_df.columns
        required_cols = ['modern_name', 'latitude', 'longitude']
        for col in required_cols:
            if col not in columns:
                message.append('{} does not appear in this'
                               'gazetteer.'.format(col))
                no_flag = False
        if no_flag:
            message.append('The gazetteer has the proper column names.\n')
        self.error_checks += message
        print(message)
        return no_flag

    def _verify_lat_long(self):
        """
        This function does not check the accuracy of any particular latitude
        and longitude.  It only checks that they are numbers that might
        actually be latitude and longitude and that the columns are in fact
        numbers.  Any mistakes or mis-entered rows are returned as a list of
        errors.  The function also prevents the object from proceeding
        with name lookups or other functions.
        """
        no_flag = True
        message = ["Lat-Long results for {}:".format(self.name)]
        try:
            # Checks for out of bounds numbers in the lat/long coordinates
            bad_lats = self.gaz_df[(90 < self.gaz_df['latitude']) |
                        (self.gaz_df['latitude'] < -90)]
            bad_longs = self.gaz_df[(180 < self.gaz_df['longitude']) |
                        (self.gaz_df['longitude'] < -180 )]
            # Out of bounds numbers set the flag to False
            if not (bad_lats.empty and bad_longs.empty):
                no_flag = False
            if bad_lats.empty:
                message.append("There are no out of bounds latitudes.")
            else:
                # Note: the index is upped by 2 to match spreadsheet programs
                message.append('The following entries have bad latitudes: '
                               '\n{}'.format((bad_lats.index + 2).tolist()))
            if bad_longs.empty:
                message.append('There are no out of bounds longitudes.\n')
            else:
                message.append('The following entries have bad longitudes: '
                               '\n{}'.format((bad_longs.index + 2).tolist()))
        # Non-numeric lat/longs produce a TypeError, are flagged and return
        # False to prevent other functions from crashing from the same error.
        except TypeError:
            # The coerce feature of to_numeric forces non-numbers to NaN's
            self.gaz_df['latitude'] = pd.to_numeric(self.gaz_df[
                                        'latitude'], errors='coerce')
            lat_0 = self.gaz_df[self.gaz_df['latitude'].isna()].index
            self.gaz_df['longitude'] = pd.to_numeric(self.gaz_df[
                                        'longitude'], errors='coerce')
            long_0 = self.gaz_df[self.gaz_df['longitude'].isna()].index
            message.append('Latitudes in row(s): \n {} \n and Longitudes in '
                    'row(s): \n{}\n are not numerals, please fix before '
                    'proceeding.'.format((lat_0 + 2).tolist(),
                                         (long_0 + 2).tolist()))
            no_flag = False
        self.error_checks += message
        print(message)
        return no_flag
