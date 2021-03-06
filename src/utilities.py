#Downcast in order to save memory

def downcast(df,date_format):
    import numpy as np
    import pandas as pd
    cols = df.dtypes.index.tolist()
    types = df.dtypes.values.tolist()
    for i,t in enumerate(types):
        if 'int' in str(t):
            df[cols[i]] = pd.to_numeric(df[cols[i]], downcast='integer')
        elif 'float' in str(t):
            df[cols[i]] = pd.to_numeric(df[cols[i]], downcast='float')
        elif t == np.object:
            if cols[i] == 'date':
                df[cols[i]] = pd.to_datetime(df[cols[i]], format=date_format)
            else:
                df[cols[i]] = df[cols[i]].astype('category')
    return df  


# This is pseudocode; made a few changes to bring it closer to completion, but can't guarantee this works
def compress_dataframe(df):
    """
    Downcast dataframe and convert objects to categories to save memory
    """
    import numpy as np

    def handle_numeric_downcast(array, type_):
        return pd.to_numeric(array, downcast=type_)

    numeric_lookup_dict = {
        "integer" : np.integer,
        "float" : np.floating,
        "object" : "object"
    }

    for type_ in ["integer", "float", "object"]:
        column_list = df.select_dtypes(include=numeric_lookup_dict[type_])

        if type_ == 'object':
            df[column_list] = df[column_list].astype('category') 
        else:
            df[column_list] = handle_numeric_downcast(df[column_list], type_)


#TODO when splitting up tasks in multiple functions, ask if it makes the code easier or harder to read. 
# IMO, these splits make the code harder to understand

#I tried upsampling in order to find the weeks that are missing by adding those rows in and filling them in with NaN
#However, for some reason, after '2011-01-31' instead of '2011-02-07', it starts with '2011-02-06' so it throws it off
#TODO can you show me screenshots of what you mean? the data was aggregated using W-MON format, maybe that will solve your issue
#TODO don't hardcode things like date formats since they're likely to change
#TODO don't need parentheses around return (minor style issue)


#The following function is quite inefficient since it has quadratic runtime O(n^2), but I'm not sure how to fix this
def find_missing_weeks_in_entire_dataframe(dataframe):
    #TODO if you'll never use any of these functions again, define them within the scope of this function so they aren't hanging out in memory
    def find_item_and_store_combo(dataframe, store_id, item_id):
        #TODO nice job on the descriptive variable names!
        #TODO hardcoding
        #TODO why cast to a dict only to cast it back to a dataframe? seems like there's a better way
        return dataframe[(dataframe['store_id'] == store_id) & (dataframe['item_id'] == item_id)]
    
    def upsampling(dataframeinput):
        return dataframeinput.set_index('datetime').resample('w').asfreq()
    
    def find_missing_weeks_for_specific_combo(dataframeinput):
        return dataframeinput[dataframeinput['dept_id'].isna()]

    combo_dict = dataframe.groupby(['store_id', 'item_id']).groups.keys()
    for key in combo_dict: 
        combo = find_item_and_store_combo(dataframe, key[0], key[1])
        upsampled = upsampling(combo)
        print(find_missing_weeks_for_specific_combo(upsampled))

    #TODO after you upsample and fill the missing rows with NaNs, you should be able to use .grouby(grouping_cols).count() to get the number of missing. no for-loops!


#Write a function to calculated MAPE weighted by the total sales for a given item across all stores
#TODO function should take two series (real and predict) and work for all items
#TODO function should calculate the MAPE for each row just like you've done below, but should take a weighted mean based on your 'real' column 
# (we'll ignore hierarchical elements for now)
def calc_mape(real, predict):
    import numpy as np
    return np.mean(np.abs((real - predict) / (np.abs(real)+1))) * 100

def calc_rmse(real, predict):
    mse = sklearn.metrics.mean_squared_error(real, predict)
    rmse = math.sqrt(mse)

#TODO randomly sampling doesn't work for time series data; you wouldn't want to train on yesterday and tomorrow, but predict on today, right?
#NOTE nice job using indices to filter; this is the fastest way IRL
def split_df (df):
    df_copy = df.copy()
    train_set = df_copy.sample(frac=0.6, random_state=0)
    test_set = df_copy.drop(train_set.index).sample(frac=0.5, random_state=0)
    holdout_set = df_copy.drop(train_set.index)
    return train_set, test_set, holdout_set
   
    

    