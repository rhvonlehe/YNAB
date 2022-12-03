#! /usr/bin/env python

"""
Convert a fidelity csv file to one accepted by YNAB
"""

import csv
import sys
import re


def is_valid_inflow_outflow_record(record):
    # Use regex to retrieve date field
    # Tricky part is to cut off immediately after the year '$', otherwise you
    # get a record with a "Downloaded on xx/yy/zzzz hh:mm pm"
    retVal = None

    # Need this check to avoid lines that appear to be InflowOutflowRecord,
    # but are too short
    #
    if (len(record) >= 10):
        retVal = re.search(r'\d{2}/\d{2}/\d{4}$', record[0])

    return retVal


def convert_record(record):
    # Reduce unwanted fields.  Tricky part: if the transaction amount field
    # is negative (outflow), leave it in the 2nd to last position.  If 
    # it's positive, move it to the last position (inflow)
    #
    newRecord = record[0:2]
    newRecord += ['', '']

    if float(record[10] == ''):
        # Avoid error trying to convert string to float below
        newRecord += ['', '0']
    elif float(record[10]) < 0:
        print('processing negative')
        newRecord += [str(abs(float(record[10]))), '']
    else:
        print('processing positive')
        newRecord += ['', record[10]]
    print(newRecord)
    return newRecord


def convert_csv_file(argv):
    # Goal of this program is to read in line-by-line a csv file in the 
    # fidelity-standard format. Convert it to the expected YNAB format:
    # Date,Payee,Category,Memo,Outflow,Inflow
    # 07/25/10,Sample Payee,,Sample Memo for an outflow,100.00,
    # 07/26/10,Sample Payee 2,,Sample memo for an inflow,,500.00
    #
    # Method: open the file using a cvsreader, massage it, write it back using
    # a cvswriter.  How do you skip over empty lines and text lines and only
    # convert those that have meaningful transactions?  
    #
    with open(argv[0]) as fidelityFile:

        with open('out.csv', mode='wt', encoding="utf-8", newline='') as ynabFile:
            fidelityReader = csv.reader(fidelityFile)   
            ynabWriter = csv.writer(ynabFile)
            ynabWriter.writerow(['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow'])
            for record in fidelityReader:
                # Is the record a transaction?  Parse it for a recognizable date
                #
                if (record):
                    if is_valid_inflow_outflow_record(record):
                        print(record)
                        # Found record with date, now convert it and add to
                        # outgoing data
                        #
                        newRecord = convert_record(record)
                        ynabWriter.writerow(newRecord)


if __name__ == "__main__":
    convert_csv_file(sys.argv[1:])
