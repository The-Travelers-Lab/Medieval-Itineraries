"""
-*- coding: utf-8 -*-

interactive_gaz_itin_commands.py

This is a set of commands to run the gazetteer_class and itinerary_class
python modules.  It includes line-by-line instructions of where to change
particular names and items to have everything run correctly.

GO TO MAIN(): to enter your particular information to run the functions.
Most of the functions can be run sequencially if desired, especially within
only itinerary functions or only gazetteer functions.

Dependencies:
    gazetteer_class.py
    itinerar_class.py
    geonames_lookup_class.py (a sub-dependency of the gazetteer_class)
    And the following python modules:
        pandas
        levenshtein
        requests
        json
        pyproj
        datetime

@author: Adam Franklin-Lyons
    Marlboro College | Python 3.7

Created on Tue Jul  2 13:36:40 2019
"""

from gazetteer_class import Gazetteer
from itinerary_class import Itinerary
import pandas as pd

Command_Dict = {'process a gazetteer': 'run_gaz',
                    'main gazetteer filename': 'gaz_file',
                    'geonames login id': 'geonames_id',
                    'compare gazetteers': 'comp_gazs',
                    'reference gazetteer filename': 'ref_gaz_file',
                    'save output gazetteer': 'save_gaz',
                    'lookup geonames ids': 'check_ids',
                    'secondary geonames lookup': 'double_ids',
                    'populate itinerary ids': 'itin_ids',
                    'itinerary id code': 'itin_code',
                    'itinerary file for reference': 'ref_itin_file',
                    'gazetteer errors to file': 'g_error_output',
                    'filename for gazetteer errors': 'g_error_file',
                    'save final gazetteer as': 'final_save',
                    'process an itinerary': 'run_itin',
                    'main itinerary filename': 'itin_file',
                    'itinerary has latitude and longitude': 'lat_long',
                    'lookup names in gazetteer': 'fuzz_match',
                    'lookup attributes in gazetteer': 'atr_lookup',
                    'lookup gazetteer filename': 'itin_gaz_file',
                    'attribute list to lookup': 'attribute_list',
                    'format dates in single column': 'form_dates',
                    'output itinerary as gazetteer': 'itin_to_gaz',
                    'gazetteer output filename': 'gaz_file_out',
                    'output itinerary as trips frame': 'itin_to_trips',
                    'keep all date columns in trips': 'keep_dates',
                    'trips dataframe output filename': 'trips_file',
                    'itinerary errors to file': 'i_error_output',
                    'filename for itinerary errors': 'i_error_file',
                    'save final itinerary as': 'final_itin_save'}

def main():
    use_file = True
    data_file_name = 'gazetteer_and_itinerary_functions_list1.txt'
    if use_file:
        data_from_file(data_file_name)

def data_from_file(file_name):
    """
    Reads in a text file with a series of lines that form the answers to the
    various questions above and create the dictionary for the Gazetteer and
    Itinerary functions to all run.
    """
    try:
        input_file = open(file_name, "r")
        input_text = input_file.readlines()
        input_text = input_text[input_text.index('Gazetteer Functions:\n')+1:]
        choice_dict = {}
        for line in input_text:
            key, value = function_names(line)
            choice_dict[key] = value
        choice_dict['attribute_list'] = choice_dict['attribute_list'
                                                       ].split(',')
        if choice_dict['run_gaz'] == True:
            gaz_functions(choice_dict)
        if choice_dict['run_itin'] == True:
            itin_functions(choice_dict)
        print_choices(choice_dict)
    except OSError:
        print('One of your file names is not valid.  Please try again.')

def function_names(line):
    choice = line.split(':')
    key_txt = choice[0].strip()
    try:
        if choice[1].strip().lower() == 'yes':
            value = True
        elif choice[1].strip().lower() == 'no':
            value = False
        else:
            value = choice[1].strip()
        if choice[0] == 'Itinerary Functions':
            return None, None
        return Command_Dict[key_txt], value
    except KeyError:
        print('The line: "{}" was not in the commands dictionary. '
              'please check the commands template.'.format(choice[0]))
        return None, None
    except IndexError:
        return None, None

def print_choices(choice_dict):
    print('You chose the following options (check for errors...):')
    for line in choice_dict.items():
        original = next((a for a, b in Command_Dict.items()
                            if b == line[0]), 'blank line')
        lineout = original + ': ' + str(line[1])
        print(lineout)

def gaz_functions(choice_dict):
    """
    This function calls the particular functions from the Gazetteer module.
    This is the choice list:
    run_gaz - (T/F)
    gaz_file - <str>
    geonames_id - <str>
    comp_gazs - (T/F)
    ref_gaz_file - <str>
    save_gaz -  - <'save', 'both', or 'merge'>
    check_ids - (T/F)
    double_ids - (T/F)
    itin_ids - (T/F)
    itin_code - <str>
    ref_itin_file - <str>
    g_error_output - (T/F)
    g_error_file - <str>
    """
    main_gaz = Gazetteer(choice_dict['gaz_file'], choice_dict['geonames_id'])
    if choice_dict['comp_gazs'] == True:
        if choice_dict['save_gaz'] == 'save':
            main_gaz.check_existing_gaz(choice_dict['ref_gaz_file'],
                                        save=True)
        elif choice_dict['save_gaz'] == 'both':
            main_gaz.check_existing_gaz(choice_dict['ref_gaz_file'],
                                        save='both')
        elif choice_dict['save_gaz'] == 'merge':
            main_gaz.check_existing_gaz(choice_dict['ref_gaz_file'],
                                        merge=True)
    if choice_dict['double_ids'] == True:
        main_gaz.geoname_id_lookup(number='double')
    elif choice_dict['check_ids'] == True:
        main_gaz.geoname_id_lookup()
    if choice_dict['itin_ids'] == True:
        itin = Itinerary(choice_dict['ref_itin_file'])
        main_gaz.itinerary_labels(itin.itin_df, choice_dict['itin_code'])
    if choice_dict['final_save'] == '<same>':
        main_gaz.csv_output()
    else:
        main_gaz.csv_output(out_file_name=choice_dict['final_save'])
    if choice_dict['g_error_output'] == True:
        main_gaz.error_output(tofile=True,
                              filename=choice_dict['g_error_file'])

def itin_functions(choice_dict):
    """
    This function calls the particular functions from the Itinerary module.
    This is the list of choices and their datatype:
    run_itin - (T/F)
    itin_file - <str>
    lat_long - (T/F)
    fuzz_match - (T/F)
    itin_gaz_file - <str>
    attribute_list - <list>
    form_dates - (T/F)
    itin_to_gaz - (T/F)
    gaz_file_out - <str>
    itin_to_trips - (T/F)
    keep_dates - (T/F)
    trips_file - <str>
    i_error_output - (T/F)
    i_error_file - <str>
    final_itin_save - <str>
    """
    main_itin = Itinerary(choice_dict['itin_file'],
                          latlong=choice_dict['lat_long'])
    if (choice_dict['fuzz_match'] == True or
        choice_dict['atr_lookup'] == True):
        ref_gaz = Gazetteer(choice_dict['itin_gaz_file'],
                            choice_dict['geonames_id'])
        if choice_dict['fuzz_match'] == True:
            main_itin.fuzzy_gaz_name_match(ref_gaz.gaz_df)
        if choice_dict['atr_lookup'] == True:
            errors = main_itin.attribute_lookup(ref_gaz.gaz_df,
                                            choice_dict['attribute_list'])
            print(errors)
    if choice_dict['form_dates'] == True:
        main_itin.format_dates()
    if choice_dict['itin_to_gaz'] == True:
        itin_gaz_df = main_itin.itin_to_gaz()
        itin_gaz_df.to_csv(choice_dict['gaz_file_out'], index=False)
    if choice_dict['itin_to_trips'] == True:
        if choice_dict['keep_dates'] == True:
            itin_trips_df = main_itin.itin_to_trips(date_style='all')
        else:
            itin_trips_df = main_itin.itin_to_trips()
        itin_trips_df.to_csv(choice_dict['trips_file'], index=False)
    if choice_dict['final_itin_save'] == 'same':
        filename = (main_itin.name + '_processed.csv')
        main_itin.itin_df.to_csv(filename, index=False)
    else:
        main_itin.itin_df.to_csv(choice_dict['final_itin_save'], index=False)
    if choice_dict['i_error_output'] == True:
        main_itin.error_output(tofile=True,
                              filename=choice_dict['i_error_file'])

main()
