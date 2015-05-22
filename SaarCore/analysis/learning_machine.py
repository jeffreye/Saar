from analysis.evaluation  import evaluator
#from analysis.evaluation import parallel_evaluator as evaluator
from data.scheme import scheme
import copy
from pandas import DataFrame
from pandas import read_csv
from os.path import isfile
import csv

learning_progres_csv = 'learning_progres.csv'

class learning_machine(object):
    """description of class"""

    def __init__(self,scheme,from_date,to_date,independent_parameter = False):
        self.from_date = from_date
        self.to_date = to_date
        self.scheme = scheme

    def generate_all_schemes(self):
        '''generate scehemes that covers all parameter ranges'''
        for i in self.scheme.indicators:
            for p in i.description.generate_all_parameters(i.parameter_count):
                new_scheme=copy.copy(self.scheme)
                indicator = copy.copy(i)
                indicator.parameter = p
                new_scheme.indicators = [indicator]
                new_scheme.name = str(indicator)
                yield new_scheme

    def calculate_top_10_solutions(self):
        '''calcualte all schemes and select top 10 solutions'''
        
        columns = ['name','rate','money']

        if isfile( learning_progres_csv ):
            scheme_profit = read_csv(learning_progres_csv)
        else:
            scheme_profit = DataFrame(columns = columns)            
        scheme_profit.set_index('name',inplace = True)

        with open(learning_progres_csv, 'w+') as csvfile:
            writer = csv.DictWriter(csvfile,delimiter=',',fieldnames = columns)
            writer.writeheader()
            for sc in self.generate_all_schemes():
                if sc.name not in scheme_profit.index:
                    e = evaluator(sc,self.from_date,self.to_date)
                    scheme_profit.ix[sc.name] = rate,money = e.calculate()
                    writer.writerow({'name':sc.name,'rate':rate,'money':money})
                    csvfile.flush()
                    print(sc.name + ' - ' + str(money) + ' \t rate = ' + str(rate))
                else:
                    writer.writerow({'name':sc.name,'rate':scheme_profit.rate[sc.name],'money':scheme_profit.money[sc.name]})
                    print(sc.name + ' - ' + str(scheme_profit.money[sc.name]) + ' \t rate = ' + str(scheme_profit.rate[sc.name]))
                    csvfile.flush()

        #return 10 solutions
        scheme_win_rates.sort('')
        return scheme_win_rates[-10:].to_dict()

    def continual_learning(self):
        '''reorder best solution from top 10 solutions'''
        pass


