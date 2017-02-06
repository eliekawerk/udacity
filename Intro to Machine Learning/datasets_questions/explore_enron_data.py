#!/usr/bin/python

""" 
    Starter code for exploring the Enron dataset (emails + finances);
    loads up the dataset (pickled dict of dicts).

    The dataset has the form:
    enron_data["LASTNAME FIRSTNAME MIDDLEINITIAL"] = { features_dict }

    {features_dict} is a dictionary of features associated with that person.
    You should explore features_dict as part of the mini-project,
    but here's an example to get you started:

    enron_data["SKILLING JEFFREY K"]["bonus"] = 5600000
    
"""

import pickle
import math

enron_data = pickle.load(open("../final_project/final_project_dataset.pkl", "r"))


enron_data_values = enron_data.values()

# print len(filter( lambda x: x['poi']==True, enron_data_values ))
# print len([item for item in enron_data_values if item['poi'] == True])


d  = filter( lambda x: x['total_payments'] == 'NaN', enron_data_values )
print d[0]
print len(d)
print len(enron_data_values)

print float(len(d)) / len(enron_data_values) * 100


