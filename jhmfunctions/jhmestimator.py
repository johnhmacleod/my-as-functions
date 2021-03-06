import logging
import datetime as dt
import numpy as np
from collections import OrderedDict
from sklearn import linear_model, ensemble, metrics, neural_network
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from iotfunctions.base import BaseTransformer
from iotfunctions.db import Database
from iotfunctions.pipeline import CalcPipeline, PipelineExpression
from iotfunctions.base import BaseRegressor, BaseEstimatorFunction, BaseClassifier
from iotfunctions.bif import IoTAlertHighValue
from iotfunctions.metadata import Model
from iotfunctions import ui

logger = logging.getLogger(__name__)

PACKAGE_URL = 'git+https://github.com/johnhmacleod/my-as-functions.git@'


class JHMSimpleAnomalyX(BaseRegressor):
    '''
    Sample function uses a regression model to predict the value of one or more output
    variables. It compares the actual value to the prediction and generates an alert 
    when the difference between the actual and predicted value is outside of a threshold.
    '''
    #class variables
    train_if_no_model = True
    estimators_per_execution = 3
    num_rounds_per_estimator = 3
    def __init__(self, features, targets, threshold,
                 predictions=None, alerts = None):
        super().__init__(features=features, targets = targets, predictions=predictions)
        if alerts is None:
            alerts = ['%s_alert' %x for x in self.targets]
        self.alerts = alerts
        self.threshold = threshold
        #registration
        self.inputs = ['features','target']
        self.outputs = ['predictions','alerts']
        self.constants = ['threshold']
        
    def execute(self,df):
        
        df = super().execute(df)
        for i,t in enumerate(self.targets):
            prediction = self.predictions[i]
            df['_diff_'] = (df[t] - df[prediction]).abs()
            alert = IoTAlertHighValue(input_item = '_diff_',
                                      upper_threshold = self.threshold,
                                      alert_name = self.alerts[i])
        df = alert.execute(df)
        
        return df
    
    @classmethod
    def build_ui(cls):
        #define arguments that behave as function inputs
        inputs = []
        inputs.append(ui.UIMultiItem(
                name = 'features',
                datatype=float,
                description = "Data items to use as features")
                      )        
        inputs.append(ui.UIMultiItem(
                name = 'targets',
                datatype=float,
                description = "Data items to use as targets")
                      )        
        inputs.append(ui.UISingle(
                name = 'threshold',
                datatype=float)
                      )
        outputs = []
        outputs.append(ui.UIFunctionOutMulti(
                name = 'predictions',
                datatype = float,
                cardinality_from = 'targets',
                description = 'Output predictions')
                       )
        outputs.append(ui.UIFunctionOutMulti(
                name = 'alerts',
                datatype = bool,
                cardinality_from = 'targets',
                description = 'Alert outputs')
                       )
                      
        return (inputs,outputs)



class JHMSimpleRegressor(BaseRegressor):
    '''
    Sample function that predicts the value of a continuous target variable using the selected list of features.
    This function is intended to demonstrate the basic workflow of training, evaluating, deploying
    using a model. 
    '''
    #class variables
    train_if_no_model = True
    estimators_per_execution = 3
    num_rounds_per_estimator = 3
    def __init__(self, features, targets, predictions=None):
        super().__init__(features=features, targets = targets, predictions=predictions)
        #registration
        self.inputs = ['features','target']
        self.outputs = ['predictions']
        

class JHMSimpleClassifier(BaseClassifier):
    '''
    Sample function that predicts the value of a discrete target variable using the selected list of features.
    This function is intended to demonstrate the basic workflow of training, evaluating, deploying
    using a model. 
    '''
    eval_metric = staticmethod(metrics.accuracy_score)
    #class variables
    train_if_no_model = True
    estimators_per_execution = 3
    num_rounds_per_estimator = 3
    def __init__(self, features, targets, predictions=None):
        super().__init__(features=features, targets = targets, predictions=predictions)
        #registration
        self.inputs = ['features','target']
        self.outputs = ['predictions']
        
class JHMSimpleBinaryClassifier(BaseClassifier):
    '''
    Sample function that predicts the value of a discrete target variable using the selected list of features.
    This function is intended to demonstrate the basic workflow of training, evaluating, deploying
    using a model. 
    '''
    eval_metric = staticmethod(metrics.f1_score)
    #class variables
    train_if_no_model = True
    estimators_per_execution = 3
    num_rounds_per_estimator = 3
    def __init__(self, features, targets, predictions=None):
        super().__init__(features=features, targets = targets, predictions=predictions)
        #registration
        self.inputs = ['features','target']
        self.outputs = ['predictions']
        for t in self.targets:
            self.add_training_expression(t,'df[%s]=df[%s].astype(bool)' %(t,t))


class MultiplyByFactorJHM(BaseTransformer):
    '''
        Sample function to scale some inputs by a factor
        '''
    def __init__(self, input_items, factor, output_items):

        self.input_items = input_items
        self.output_items = output_items
        self.factor = float(factor)
        super().__init__()
    def execute(self, df):
        df = df.copy()
        for i,input_item in enumerate(self.input_items):
            df[self.output_items[i]] = df[input_item] * self.factor
        return df

    @classmethod
    def build_ui(cls):
        #define arguments that behave as function inputs
        inputs = []
        inputs.append(ui.UIMultiItem(
                name = 'input_items',
                datatype=float,
                description = "Data items adjust",
                output_item = 'output_items',
                is_output_datatype_derived = True)
                      )
        inputs.append(ui.UISingle(
                name = 'factor',
                datatype=float)
                      )
        outputs = []
        return (inputs,outputs)

