"""
-*- coding: utf-8 -*-

itinerary_class.py

Init creates a dataframe of itinerary information with a few required columns:
['modern_name', 'day', 'month', 'year']  'latitude' and 'longitude are also
helpful, but can also be filled in with a Gazetteer if desired.

Variables List:
    self.itin_df - the pandas dataframe of data read in for the itinerary
    self.no_flag - a True/False value used as a gate if there are correct
        columns and other attributes in the dataframe
    self.error_checks - a List of trings that encode various smaller errors
        discovered in the dataframe (missing cells of data, bad date formats,
        lookup failures in gazetteer dataframes, etc.)  Can be printed with
        the "error_output" function.
    self.latlong - tracks whether the itin_df includes latitude and longitude
        data; is a True/False value
    self.name - a truncated version of the input filename used for default
        output files and error message txt files.

Function List:
    fuzzy_gaz_name_match(self, gaz_df):
        This function adds a column to the itinerary dataframe that labels
        each name in the modern_name column with the highest matching ratio
        name in the gazetteer.
    attribute_lookup(self, gazetteer_dataframe, attributes):
        This function takes a separate gazetteer and identifies the named
        attribute in the gazetteer for each row in the itinerary.  It creates
        a new column in the Itinerary with that information, leaving a None
        if no entry is found in the Gazetteer.
    format_dates(self):
        Takes the day, month, and year columns and creates a date(yyyy-mm-dd)
        cell in a new column for every row.  The new dataframe drops any
        NaN rows missing date information
    itin_to_gaz(self):
        Takes every unique location in the Itinerary and creates a Gazetteer
        dataframe for export.  If the itinerary includes Lat/Long or geo_ids
        these are included in the output dataframe.
    itin_to_trips(self, date_style='full_date'):
        Separates out all individual trips in the itinerary, ignoring blanks
        and repeated locations.  The output dataframe has origin and
        destination columns for date, name, lat, long, and geo_id.  The output
        can be done with full dates (which uses format_dates prior to running)
        or can be run leaving in day/month/year columns.  Using 'months' for
        date_style returns only months and days (not recommended for trips).
        Using full_date returns formatted dates; using 'all' returns formatted
        dates but also maintains the day/month/year columns.
    error_output(self, tofile=False, filename=None):
        This creates a txt file with all errors accumulated in running the
        various functions.  It will record specific line errors for problems
        arrising from looking up data in a Gazetteer to formating dates.  If
        tofile remains False, the output will be in the interactive python
        session.  If filename remains None, a default based on the original
        itinerary file name is created.

Functions called by main Function List:
    def _max_lev(self, itin_name, gaz_df):
        Takes a name and a dataframe with a 'modern_name' column and compares
        the name to every entry in the modern_name column.  It retuns the
        best ratio match in the column.  If there is an exact match, instead
        of the name it enters 'exact match,' if there is no match better than
        50% it enters a None.
    _gaz_lookup(self, gaz_df, attribute, row_index, column='modern_name'):
        Looks up the desired attribute where the row_index matches the
        modern_name column (or other column as desired - modern_name is the
        current default)
    _date_formater(self, row):
        takes the day, month, and year and returns a single date(yyyy-mm-dd)
    _trips_date_style(self, date_style):
        Determines whether the trips dataframe will be output with fully
        formatted dates or only month and year columns. (accepts 'month',
        'full_date', or 'all').
    _undated_locations(self):
        Records all rows in which there is a location listed without a
        complete date.  These locations are dropped if date_style is full_date
        but will be kept in the 'month' style.
    _distance_calc(self, trip_row):
        Returns a great circle distance between two pairs of lat/long
        coordinates, called as part of the trips dataframe.
    _verify_cols(self):
        Only checks if all columns needed in other functions exist and have
        the proper names - returns an error and prevents other functions
        from running if they are not.

Possible inclusions:
    A) The Itinerary Analysis functions might be streamlined and
included although currently they are not.  The functions themselves are too
long and based largely on the 'modern_name' row, which is stripped out and
acted on separately - reincorporating that to a pandas DF based class should
be the next step.
    B) Set a general "reference column" variable that can be used to match
columns with other dataframes - right now this is basically taken by the
'modern_name' column and is often fixed.  It should be a transmitted variable
that can more easily be set in several functions.  ('modern_name' is the
reference more than a dozen times...)

@author: Adam Franklin-Lyons
    Marlboro College | Python 3.7

Created on Tue May 21 20:27:31 2019
"""

import pandas as pd
import datetime as dt
from numpy import cos, sin, arcsin, sqrt, radians
# from pyproj import Geod
import Levenshtein as lev

class Itinerary:

    def __init__(self, file_name, latlong=False):
        """Import a gazetteer file into a Pandas DataFrame"""
        self.itin_df = pd.read_csv(file_name, error_bad_lines=False,
                                     encoding='utf-8-sig')
        self.name = file_name.split('.')[0]
        self.latlong = latlong
        self.no_flag, self.error_checks = self._verify_cols()

    def fuzzy_gaz_name_match(self, gaz_df):
        """
        For each modern_name in the itinerary, this function adds a column
        to the itinerary dataframe that has the highest matching ratio
        name in the gazetteer.
        """
        values = self.itin_df['modern_name'].notna()
        self.itin_df['gaz_match'] = self.itin_df.loc[values,
                                            'modern_name'].apply(lambda x:
                                            self._max_lev(x, gaz_df))

    def _max_lev(self, itin_name, gaz_df):
        """
        Takes a name and a dataframe with a 'modern_name' column and compares
        the name to every entry in the modern_name column.  It retuns the
        best ratio match in the column.  If there is an exact match, instead
        of the name it enters 'exact match,' if there is no match better than
        50% it enters a None.
        """
        name_series = gaz_df['modern_name'].apply(str)
        lev_series = name_series.apply(lambda x: lev.ratio(x.lower(),
                                                 str(itin_name).lower()))
        max_lev = lev_series.max()
        if max_lev == 1:
            name = 'exact match'
        elif max_lev > 0.5:
            row_num = lev_series.idxmax()
            name = gaz_df.loc[row_num, 'modern_name']
        else:
            name = None
        return name

    def attribute_lookup(self, gaz_df, attributes):
        """
        The input gazetteer needs to include a column that has matched names
        from the itinerary dataframe.  Generally, this will be something like
        'modern_name' or 'geo_id'.  The function creates new columns for
        latitude and longitude in the itinerary dataframe, searches the
        gazetteer list for each element in the itinerary dataset, and inputs
        the data for all matches.  Columns in the itinerary frame that do not
        find a match in the gazetteer are compiled as a list of strings that
        note the column and name of the location not found in the gazetteer.
        The function returns the modified itinerary dataframe along with the
        list of errors.
        Place Lat and Long as columns in the itin_frame from gaz_frame
        Return modified itin_frame
        """
        blanks = self.itin_df[self.itin_df['modern_name'].isna()].index
        message = []
        # Attributes can be either string or list - this forces a list.
        try:
            attributes = attributes.split()
        except AttributeError:
            attributes = list(attributes)
        # Checks that the attributes match column names in the Gazetteer.
        for name in attributes:
            if name in gaz_df.columns: None
            else:
                attributes.remove(name)
                message.append('The gazetteer used for the attribute lookup'
                               ' does not contain {}s.'.format(name))
        for name in attributes:
            message.append('Looking up {} in the gazetteer.'.format(name))
            self.itin_df[name] = self.itin_df['modern_name'].apply(
                    lambda x: self._gaz_lookup(gaz_df, name, x))
            # Compiles the errors where the lookup function below failed.
            errors = self.itin_df[self.itin_df[name].isna()].index
            errors = errors.difference(blanks)
            if errors.empty:
                message.append('All {}s were found.'.format(name))
            else:
                message.append('The following {}s were not in the '
                               'Gazetteer:'.format(name))
                for i in errors:
                    message.append('Error on line {}; {} \n'.format(i,
                                      self.itin_df['modern_name'][i]))
        # If latitude and longitude looked up correctly, change class variable
        if {'latitude','longitude'}.issubset(attributes):
            self.latlong = True
        self.error_checks += message
        print('See the output text file for possibe errors.')
        return message

    def _gaz_lookup(self, gaz_df, attribute, row_ref, column='modern_name'):
        """
        This function uses the modern name in the itinerary row (supplied as
        'row_ref'), and finds the gazetteer row that matches that name from
        the supplied gaz_df.  It then returns the value from the gazetteer
        row that matches the 'attribute' column.  Missing names or other
        index errors return None.  This function could theoretically be also
        used to match other columns (like geo_id) in the gazetteer dataframe.
        """
        try:
            return gaz_df.loc[gaz_df[column]==row_ref, attribute].values[0]
        except IndexError:
            return None

    def format_dates(self):
        """
        Takes the columns: year, month, day
        If all three are present, the function creates a new column 'date'
        at the beginning of the dataframe.
        The 'date' column is in the datetime type but without times.
        All incomplete dates or bad date entries will be left empty and
        logged in the "error_checks" list.
        """
        self._verify_cols()
        message = []
        # Structures dates as yyyy-mm-dd from three independent columns.
        self.itin_df['dates'] = self.itin_df.apply(lambda x:
                                        self._date_formater(x), axis=1)
        date_filter = self.itin_df[['day','month','year']].isna().any(axis=1)
        blanks = self.itin_df[date_filter].index
        message.append('The following dates are incomplete: \n{}'.format(
                                                    (blanks + 2).tolist()))
        blank_dates = self.itin_df.dates.isna()
        bad_dates = self.itin_df[blank_dates].index.difference(blanks)
        message.append('The following dates contain errors:\n{}'.format(
                                                    (bad_dates + 2).tolist()))
        cols = self.itin_df.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        self.itin_df = self.itin_df[cols]
        self.error_checks += message

    def _date_formater(self, row):
        """
        Requires a Series or Dataframe row containing 'day', 'month', and
        'year' in its index or columns and attempts to return a formatted
        date type. All entries are coerced to integers.  Any failed integer
        or bad date (ie: February 30th) returns None for the date.
        Example: {year:'1291', month:'8', day:'14'} returns
             datetime.date(1291, 8, 14)
        """
        try:
            # Forces all values in the three columns to integer for dt.date
            row = pd.to_numeric(row[['day','month','year']],
                                downcast='integer', errors='coerce')
            date = dt.date(row.year, row.month, row.day)
            return date
        # dt.date with NaN instead of numeric values throws a TypeError
        except TypeError:
            return None
        # Days out of range (July 34th, etc) throw a ValueError
        except ValueError:
            print('{} has a date value out of range.'.format(row.name))
            return None

    def itin_to_gaz(self):
        """
        Converts an itinerary into a gazetteer.  The function takes all unique
        entries in the itinerary, attaches their latitude and longitude (if
        present), drops date columns, and creates standard gazetteer columns
        (certainty, checked, modern_country).  If there are no lat/long
        coordinates, the function prints a warning, but does not throw an
        error.  Returns a pandas DataFrame.
        """
        self._verify_cols()
        if not self.no_flag:
            print("This operation has failed")
            return None
        if not self.latlong:
            print('Warning: This gazetteer lacks lat-long coordinates')
        gaz_x = self.itin_df['modern_name'].drop_duplicates().dropna().index
        gaz_df = self.itin_df.loc[gaz_x]
        gaz_df.drop(columns=['day','month','year'], inplace=True)
        gaz_df.sort_values('modern_name', inplace=True)
        if self.latlong: cols1 = ['modern_name', 'latitude', 'longitude']
        else: cols1 = ['modern_name']
        cols2 = ['modern_country', 'checked', 'certainty']
        columns = cols1 + cols2 + gaz_df.columns.drop(cols1).tolist()
        gaz_df = gaz_df.reindex(columns, axis=1)
        if 'dates' in columns: gaz_df.drop(columns='dates', inplace=True)
        return gaz_df

    def itin_to_trips(self, date_style='full_date'):
        """
        Outputs a new dataframe with the original itinerary reorganized as
        a series of point A to point B trips.  This program works best when
        there are not a lot of gaps in the data, as large gaps will appear in
        the output as single very long trips (if someone is in London on March
        1 and arrives in Caterbury on April 2, this will return a "trip"
        taking a month from London to Caterbury, whether or not the person was
        actually in London for the remainder of that time.) The trips maintain
        the name, date, geo_id, latitude, and longitude columns when
        available.  The csv may include other columns such as notes or
        original names or source references, but these will not appear in the
        output.  The function requires 'latitude' and 'longitude' columns
        largely filled in and will stop the function and return an error
        message if they are not available.  'date_style' can be 'full_date'
        (the default), 'months' or 'all'.  'full_date' only uses entries with
        days, months and years available and drops all others.  'all' uses
        only full dates, but keeps the other columns.  'month' which keeps
        all rows containing a month regardless of the day column.

        Output format -

        csv filw with the following headings:
            depart_date (yyyy-mm-dd)
            depart_loc (str) - based on modern_name from inputs
            depart_id (str)
            depart_lat (decimal)
            depart_long (decimal)
            arrive_date (yyyy-mm-dd)
            arrive_loc (str) - same as above
            arrive_id (str)
            arrive_lat (decimal)
            arrive_long (decimal)
            travel_days (int) - recorded as number of days
            distance (decimal) - the straight line distance in kilometers
                        between the two points
        """
        self._verify_cols()
        # Prevents function from running without latitude and longitude
        if (not self.latlong) or self.itin_df.latitude.empty:
            print('This Itinerary is lacking coordinates please create a '
                  '"latitude" and "longitude" column before proceeding.')
            return None
        # determines whether to include full dates or day, month, year columns
        date_col, ref = self._trips_date_style(date_style)
        # If there are no date columns, the function fails...include message?
        if not date_col: return None
        # The 'ref' only drops columns with missing days rather than months
        dated_locs = self.itin_df[date_col[:ref] +
                                  ['modern_name']].notna().all(axis=1)
        columns = date_col + ['modern_name','latitude','longitude']
        if 'geo_id' in self.itin_df.columns: columns.append('geo_id')
        trip_df = self.itin_df[dated_locs].reindex(columns=columns)
        # Lines up the database in dated order so trips are contiguous.
        trip_df.sort_values(date_col[:ref], kind='mergesort', inplace=True)
        # This pair removes all repeated locations to leave trips only.
        orig_df = trip_df[trip_df.modern_name.shift(-1)!=trip_df.modern_name]
        dest_df = trip_df[trip_df.modern_name.shift(1)!=trip_df.modern_name]
        df_lst = [orig_df.reset_index(drop=True),
                  dest_df.reset_index(drop=True).shift(-1)]
        trip_df = pd.concat(df_lst, axis=1).loc[df_lst[0].index[:-1]]
        # Relabeling columns for the 'trips' - origin and destination.
        origin_cols = ['origin_' + col for col in columns]
        dest_cols = ['dest_' + col for col in columns]
        trip_df.columns = origin_cols + dest_cols
        # months style prioritizes years and months and cannot calculate the
        # day vector between origin and destination dates.
        if date_style!='months':
            trip_df['travel_days'] = (trip_df['dest_dates'] -
                                   trip_df['origin_dates']).dt.days
        trip_df['distance'] = trip_df.apply(self._distance_calc, axis=1)
        return trip_df

    def _trips_date_style(self, date_style):
        """
        Determines whether the trips dataframe will be output with fully
        formatted dates or only month and year columns.
        """
        if date_style=='full_date' or date_style=='all':
            # Creates an integrated 'dates' field from the year-month-day.
            if 'dates' not in self.itin_df.columns:
                self.format_dates()
                message = self._undated_locations()
                self.error_checks += message
                if message:
                    print('Some locations are missing due to missing dates - '
                         'check errors in error_checks or error output file.')
        if date_style=='full_date':
            date_col = ['dates']
            return date_col, 1
        elif date_style=='months':
            date_col = ['year','month','day']
            return date_col, 2
        elif date_style=='all':
            date_col = ['dates','year','month','day']
            return date_col, 1
        else:
            print('Attribute Error: the dates attribute has an out of '
                  'bounds value.')
            return None

    def _undated_locations(self):
        """
        Records all rows in which there is a location listed without a
        complete date.  These locations are dropped from the trips dataframe
        but recorded as a list in the errors output.
        """
        message = []
        no_names = self.itin_df[self.itin_df['modern_name'].isna()].index
        no_dates = self.itin_df[self.itin_df['dates'].isna()].index
        # Does not flag locations without a name...obviously.
        missing_locs = no_dates.difference(no_names)
        places = self.itin_df.loc[missing_locs, 'modern_name'].unique()
        if places:
            message.append('the following places are listed with no dates:')
            for loc in places:
                message.append('{}, '.format(loc))
            message.append('the locations are in the following rows:')
            message.append('{}.'.format((missing_locs + 2).tolist()))
        return message

    def _distance_calc(self, trip_row):
        """
        The old version uses a geo-calculator from pyproj to create a great 
        circle distance given a series, array, or row of a dataframe and 
        returns the distance:
        wgs84_geod = Geod(ellps='WGS84')
        lat1, long1 = trip_row.origin_latitude, trip_row.origin_longitude
        lat2, long2 = trip_row.dest_latitude, trip_row.dest_longitude
        az12,az21,dist = wgs84_geod.inv(long1,lat1,long2,lat2)
        kmdist = round((dist / 1000), 1)
        
        This new version is a direct calculation using the Haversine formula.
        
        The inputs from the series need to include depart_lat, depart_long,
        arrive_lat, and arrive_long.  Distance is returned in kilometers
        """
        lat1, long1 = trip_row.origin_latitude, trip_row.origin_longitude
        lat2, long2 = trip_row.dest_latitude, trip_row.dest_longitude
        long1, lat1, long2, lat2 = map(radians, [long1, lat1, long2, lat2])
        dlong = long2 - long1 
        dlat = lat2 - lat1 
        angle = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlong/2)**2
        arc_dist = 2 * arcsin(sqrt(angle)) 
        km_dist = 6367 * arc_dist
        return km_dist

    def error_output(self, tofile=False, filename=None):
        """
        Takes the errors gathered together at any point in the use of the
        specific Itinerary and outputs them either as basic print statements
        in an interactive session or prints to a txt file.  For a txt file
        print, enter: 'tofile=True' as an argument.  The default file name
        is the same as the input itinerary with '_errors.txt' added.  For a
        different label, use the argument: filename='desired_name'
        """
        output = pd.unique(self.error_checks).tolist()
        output.append('Have a nice day!')
        if tofile:
            if filename:
                error_file = filename
            else:
                error_file = self.name + '_errors.txt'
            with open(error_file, 'w') as f:
                f.writelines("{}\n".format(line) for line in output)
        else:
            for line in output:
                print(line)
        return None

    def _verify_cols(self):
        """
        Verify checks to make sure there are column names required by other
        functions.  If latitude ad longitude are present, it sets the class
        variable latlong to True which allows other processing.  Otherwise,
        it returns a message that the itinerary lacks coordinates.
        """
        no_flag = True
        message = []
        columns = self.itin_df.columns
        required_cols = ['modern_name', 'day', 'month', 'year']
        for col in required_cols:
            if col not in columns:
                message.append('"{}" does not appear in the itinerary columns'
                               '\n Please fix before continuing.'.format(col))
                no_flag = False
        if not message:
            message.append("The itinerary has the proper column names.")
        if {'latitude','longitude'}.issubset(columns):
            self.latlong = True
        else:
            message.append('Note: This itinerary lacks Lat-Long coordinates.')
        # print(message)
        return no_flag, message
