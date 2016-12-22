import numpy as np
import pandas as pd
from . import SignalDecomposition_AR as tsar
from . import Utils as tsutil

import sys


class cAbstract_Scikit_Model(tsar.cAbstractAR):
    def __init__(self , cycle_residue_name, P , iExogenousInfo = None):
        super().__init__(cycle_residue_name, iExogenousInfo)
        self.mNbLags = P;
        self.mNbExogenousLags = P;
        self.mScikitModel = None;

    def dumpCoefficients(self, iMax=10):
        # print(self.mScikitModel.__dict__);
        pass

    def build_Scikit_Model(self):
        assert(0);

    def set_name(self):
        assert(0);

    def fit(self):
        #  print("ESTIMATE_SCIKIT_MODEL_START" , self.mCycleResidueName);

        self.build_Scikit_Model();
        self.set_name();
        
        series = self.mCycleResidueName; 
        self.mTime = self.mTimeInfo.mTime;
        self.mSignal = self.mTimeInfo.mSignal;
        lAREstimFrame = self.mTimeInfo.getEstimPart(self.mARFrame)

        # print("mAREstimFrame columns :" , self.mAREstimFrame.columns);
        lARInputs = lAREstimFrame[self.mInputNames].values
        lARTarget = lAREstimFrame[series].values
        # print(len(self.mInputNames), lARInputs.shape , lARTarget.shape)
        assert(lARInputs.shape[1] > 0);
        assert(lARTarget.shape[0] > 0);

        from sklearn.feature_selection import SelectKBest
        from sklearn.feature_selection import f_regression
        lMaxFeatures = self.mOptions.mMaxFeatureForAutoreg;
        if(lMaxFeatures >= lARInputs.shape[1]):
            lMaxFeatures = lARInputs.shape[1];
        self.mFeatureSelector =  SelectKBest(f_regression, k= lMaxFeatures);
        self.mFeatureSelector.fit(lARInputs, lARTarget);
        lARInputsAfterSelection =  self.mFeatureSelector.transform(lARInputs);
        # print("FEATURE_SELECTION" , self.mOutName, lARInputs.shape[1] , lARInputsAfterSelection.shape[1]);
        del lARInputs;
        
        self.mScikitModel.fit(lARInputsAfterSelection, lARTarget)
        del lARInputsAfterSelection;
        del lARTarget;
        del lAREstimFrame;     
        
        lFullARInputs = self.mARFrame[self.mInputNames].values;
        lPredicted = self.mScikitModel.predict(lFullARInputs);
            
        self.mARFrame[self.mOutName] = lPredicted

        self.mARFrame[self.mOutName + '_residue'] =  self.mARFrame[series] - self.mARFrame[self.mOutName]

        # print("ESTIMATE_SCIKIT_MODEL_END" , self.mOutName);


    def transformDataset(self, df):
        series = self.mCycleResidueName; 
        if(self.mExogenousInfo is not None):
            df = self.mExogenousInfo.transformDataset(df);
        # print(df.columns);
        # print(df.info());
        # print(df.head());
        # print(df.tail());
        lag_df = self.generateLagsForForecast(df);
        # print(self.mInputNames);
        # print(self.mFormula, "\n", lag_df.columns);
        # lag_df.to_csv("LAGGED_ " + str(self.mNbLags) + ".csv");
        inputs = lag_df[self.mInputNames].values
        inputs_after_feat_selection = self.mFeatureSelector.transform(inputs);
        pred = self.mScikitModel.predict(inputs_after_feat_selection)
        df[self.mOutName] = pred;
        target = df[series].values
        df[self.mOutName + '_residue'] = target - df[self.mOutName].values        
        return df;



class cAutoRegressiveModel(cAbstract_Scikit_Model):
    def __init__(self , cycle_residue_name, P , iExogenousInfo = None):
        super().__init__(cycle_residue_name, P, iExogenousInfo)
        self.mComplexity = P;

    def dumpCoefficients(self, iMax=10):
        logger = tsutil.get_pyaf_logger();
        lDict = dict(zip(self.mInputNames , self.mScikitModel.coef_));
        lDict1 = dict(zip(self.mInputNames , abs(self.mScikitModel.coef_)));
        i = 1;
        lOrderedVariables = sorted(lDict1.keys(), key=lDict1.get, reverse=True);
        for k in lOrderedVariables[0:iMax]:
            logger.info("AR_MODEL_COEFF " + str(i) + " " + str(k) + " " + str(lDict[k]));
            i = i + 1;


    def build_Scikit_Model(self):
        import sklearn.linear_model as linear_model
        self.mScikitModel = linear_model.Ridge()

    def set_name(self):
        self.mOutName = self.mCycleResidueName +  '_AR(' + str(self.mNbLags) + ")";
        self.mFormula = "AR(" + str(self.mNbLags) + ")";
        if(self.mExogenousInfo is not None):
            self.mOutName = self.mCycleResidueName +  '_ARX(' + str(self.mNbLags) + ")";
            self.mFormula = "ARX(" + str(self.mNbExogenousLags) + ")";
        
        

class cSVR_Model(cAbstract_Scikit_Model):
    def __init__(self , cycle_residue_name, P , iExogenousInfo = None):
        super().__init__(cycle_residue_name, P, iExogenousInfo)
        self.mComplexity = 2*P;

    def dumpCoefficients(self, iMax=10):
        pass


    def build_Scikit_Model(self):
        import sklearn.svm as svm
        self.mScikitModel = svm.SVR(kernel='rbf')

    def set_name(self):
        self.mOutName = self.mCycleResidueName +  '_SVR(' + str(self.mNbLags) + ")";
        self.mFormula = "SVR(" + str(self.mNbLags) + ")";
        if(self.mExogenousInfo is not None):
            self.mOutName = self.mCycleResidueName +  '_SVRX(' + str(self.mNbLags) + ")";
            self.mFormula = "SVRX(" + str(self.mNbExogenousLags) + ")";