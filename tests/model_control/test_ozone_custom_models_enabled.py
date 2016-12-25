import pandas as pd
import numpy as np
import pyaf.ForecastEngine as autof
import pyaf.Bench.TS_datasets as tsds

#get_ipython().magic('matplotlib inline')


def build_model(transformations, trends, periodics, autoregs):
    b1 = tsds.load_ozone_exogenous()
    df = b1.mPastData

    lEngine = autof.cForecastEngine()
    lEngine

    H = b1.mHorizon;
    # lEngine.mOptions.enable_slow_mode();
    # lEngine.mOptions.mDebugPerformance = True;
    lEngine.mOptions.set_active_transformations(transformations);
    lEngine.mOptions.set_active_trends(trends);
    lEngine.mOptions.set_active_periodics(periodics);
    lEngine.mOptions.set_active_autoregressions(autoregs);
    lExogenousData = (b1.mExogenousDataFrame , b1.mExogenousVariables) 
    lEngine.train(df , b1.mTimeVar , b1.mSignalVar, H);
    lEngine.getModelInfo();
    print(lEngine.mSignalDecomposition.mTrPerfDetails.head());
    
    lEngine.mSignalDecomposition.mBestModel.mTimeInfo.mResolution
    
    lEngine.standrdPlots("outputs/my_ozone");
    
    dfapp_in = df.copy();
    dfapp_in.tail()

    #H = 12
    dfapp_out = lEngine.forecast(dfapp_in, H);
    #dfapp_out.to_csv("outputs/ozone_apply_out.csv")
    dfapp_out.tail(2 * H)
    print("Forecast Columns " , dfapp_out.columns);
    Forecast_DF = dfapp_out[[b1.mTimeVar , b1.mSignalVar, b1.mSignalVar + '_Forecast']]
    print(Forecast_DF.info())
    print("Forecasts\n" , Forecast_DF.tail(H));

    print("\n\n<ModelInfo>")
    print(lEngine.to_json());
    print("</ModelInfo>\n\n")
    print("\n\n<Forecast>")
    print(Forecast_DF.to_json(date_format='iso'))
    print("</Forecast>\n\n")
