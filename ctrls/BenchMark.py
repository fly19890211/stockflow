#!/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
from ctrls import *
from config import *
from os import listdir
from os.path import isfile, join

class BenchMark():
    '''To Run BenchMark on specific numbers for specific years'''

    def __init__(self, numbers, Model):
        # check the number from Database, remove error numbers
        tsecNumbers = [ n[:-4] for n in listdir(TSEC_DATA_PATH) if n[-4:] == '.csv' ]
        for number in numbers:
            if number not in tsecNumbers:
                numbers.remove(number)

        self.numbers = numbers
        self.Model = Model
        self.years = range(BENCHMARK_YEAR_START, BENCHMARK_YEAR_END + 1)

    def run(self, noLog = False):
        '''
            依照年份測試指定清單的資料。
        '''
        # Initialize BenchYearRecorder and BenchModelRecorder
        benchYearRecorders = dict()
        for year in self.years:
            benchYearRecorders[year] = BenchYearRecorder(self.Model().infos, year)

        

        for number in self.numbers:

            benchModelRecorder = BenchModelRecorder(self.Model().infos, number)

            for year in self.years:

                if not noLog: sys.stdout.write('%s  %4d' % (number, year))

                reader = Reader(number)
                model = self.Model()
                trader = Trader(model.infos, number)

                while True:

                    row = reader.getInput()
                    if row == None: break
                    
                    prediction = model.predict()
                    data_year = int(row[0].split('/')[0])

                    if data_year > year: break
                    elif data_year == year:
                        trade = trader.do(row, prediction)
                        model.update(row, trade)
                    else: model.update(row, None)

                result = trader.analysis()

                if not noLog: sys.stdout.write('\t%4.3f %%\n' % result["ROI"])

                benchYearRecorders[year].update(result)
                benchModelRecorder.update(result)

            benchModelRecorder.record()

        for year in self.years:
            benchYearRecorders[year].record()
