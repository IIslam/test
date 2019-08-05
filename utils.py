#Import Libraries
import configparser
import xlrd
import pandas as pd
import numpy as np
import csv

#from os.path import dirname, realpath
def read_training_csv(path,encoding="ISO-8859-1"):
    data = pd.read_csv(path,encoding=encoding)
    header_columns = list(data.columns.values)
    verbatim = [element.strip() for element in data[header_columns[0]]]
    label = [element.strip() for element in data[header_columns[1]]]
    return np.array(verbatim), np.array(label)

def sentence_to_words(sentence):
    return sentence.split()

def read_csv(path):
  with open(path, 'r',errors="surrogateescape") as csvfile:
    raw_data = csv.reader(csvfile, delimiter=",", quotechar='"')
    data = [row for row in raw_data]
  return data

#return list of lists , each list is a row from the excel file and return list of the header column names
def read_excel(path):
    dataframe=read_excel_file(path)

    data=dataframe.values.tolist()
    return data,list(dataframe.columns.values)


#return list contains of dictionaries, each dictionary is row in the file without the header file
#return also the header column names as a list
def read_csv_dict(path, encoding='ISO-8859-1'):
    data =read_csv(path)
    colnames = data[0]
    #print colnames
    dict_data = []
    for i in range(1, len(data)):
      row = data[i]
      new_row = {}
      for index, entry in enumerate(row):
        new_row[colnames[index]] = entry
      dict_data.append(new_row)
    fieldnames = colnames
    return dict_data, fieldnames

def read_excel_dict(path, encoding='ISO-8859-1'):
    try:
        data,colnames =read_excel(path)
        #print colnames
        dict_data = []
        for i in range(len(data)):
          row = data[i]
          new_row = {}
          for index, entry in enumerate(row):
            new_row[colnames[index]] = entry
          dict_data.append(new_row)
        fieldnames = colnames
        #gui_screen.progress(40)
        return dict_data, fieldnames
    except:
        pass
        #gui_screen.message_box("Error","Failed to read the input file")

def read_data(fileType,filePath):
    if fileType=="csv":
        verbatim,label=read_training_csv(filePath)
        return verbatim,label
    elif fileType=="json":
        pass

#To get file extension
def fileType(filePath):
    return filePath.split(".")[-1]

def parent_directory():
    pass
 #return os.getcwd()
 #return os.path.abspath(os.path.dirname(__file__))

def current_directory():
    pass
  #return os.getcwd()


#return dataframe for the excel file data
def read_excel_file(filePath):
    try:
        df = pd.read_excel(filePath)
        # lowercase header in dataframe
        df.columns = map(str.lower, df.columns)
        #df = df[np.isfinite(df['verbatim'])]
        return df
    except:
        pass
        #gui_screen.message_box("Error","Failed to read mindmap file correctly")


# Read data from config.ini file and put it in a dictionary called options
def read_options(config_path, section):
  full_path = config_path
  Config = configparser.ConfigParser()
  Config.read(full_path)
  parsed_values = {'True': True, 'False': False, 'None': None}
  options = {}
  option_keys = Config.options(section)
  for key in option_keys:
    try:
        value = Config.get(section, key)
        if value in parsed_values:
          options[key] = parsed_values[value]
        else:
          options[key] = value

    except:
        #print("exception on %s!" % key)
        options[key] = None
  return options


'''
def get_parent_root():
    filepath = realpath(__file__)

    dir_of_file = dirname(filepath)
    parent_dir_of_file = dirname(dir_of_file)
    parents_parent_dir_of_file = dirname(parent_dir_of_file)

    return parent_dir_of_file
'''
# remove dots that are not at the end of any sentence
def removeUnnecessaryDots(verbatim):
    new_verbatim=''
    flag=0
    for char in verbatim:
        if char.isalpha():
            new_verbatim+=char
            flag=1
        elif char=="." and flag==1:
            flag=0
            new_verbatim+=char+" "
        elif char==" ":
            new_verbatim+=" "
        else:
            flag=0
    return new_verbatim


def change_listoflist_to_list(listOfList):
    l=[]
    for li in listOfList:
        for word in li:
            l.append(str(word))
    l=set(l)
    l=list(l)
    return l
'''
from itertools import chain
def change_listoflist_to_list(listOfList):
    return list(set(chain.from_iterable(listOfList)))
'''

def change_listoflist_to_listofstrings(l):
    newList=[]
    for list in l:
        newList.append(','.join(list))
    return newList