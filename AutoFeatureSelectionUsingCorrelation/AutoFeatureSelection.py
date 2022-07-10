import json

def findBestFeatues(data, target_feature, collinear_threshold=None, corr_threshold=None):
    '''
    Input parameter:
    data : DataFrame : Data on which want to perform feature selection
    target_features : String : Target feature
    collinear_threshold : float : This values lies between 0 and 1. If corrleation between two features is greater than this value then those consider as collinear.
    corr_threshold : float : This values lies between 0 and 1. If corrleation between feature and target variable is smaller than this value then that feature consider as less impact on target variable. Then feature is discarded.
    
    Return:
    reduced_features : dict : Contains ignorable features those are not as per correlation and collinear threshold. Feature name is key and the reason why not to consider this feature is  value.
    corr_with_target : dict : Contains best features as per input correlation and collinear threshold. Feature name is key and its correlation with target variable is value.
    '''
    
    corr_obj = json.loads(data.corr().to_json(orient='columns'))
    # flag = True
    reduced_features = dict()
    available_features = list(corr_obj.keys())
    available_features.remove(target_feature) # Available feature does not contains target variable
    size_feature = len(available_features);
    dropFeature = set();
    i = 0;
    
    explaination_collinear = "Correlation between feature {0} and {1} is {2}. As collinear threshold is {3} hence they are collinear. As correlation of feature {0} and target variable {4} is {5} higher than the correlation between feature {1} and target variable {4} is {6}. Hence we can drop feture {1}"
    # 0 : feature1, 1 : feature2 (drop), 2: correlation between feature1 and feture2,  3 : threshold, 4 : target variable, 5 : corr between feature1 and target variable, 6 : corr between feature2 and target variable
    
    explaination_corr = "Correlation threshold is {0} and correlation between feature {1} and target variable {2} is {3}"
    # 0 : Correlation threshold, 1 : feature, 2 : target feature,  3 : Correlation between feature and target feature

    # Drop all correlation with same feature and correlation of features with target variable 
    # We will keep correlation of target variable and features in single dictionary
    for feature in corr_obj.keys():
        del corr_obj[feature][feature];
        if feature != target_feature:
            del corr_obj[feature][target_feature];
            
     
    # Remove all features those having more than threshold collinearity
    if collinear_threshold != None:
        i = 0;
        while i < size_feature:
            j = i + 1
            dropFeature = set() # Want to keep unique values
            feature1 = available_features[i]
            feature1_removed = False # check whether feture is getting removed or not

            while j < size_feature:
                feature2 = available_features[j]
                if abs(corr_obj[feature1][feature2]) >= collinear_threshold:
                    corr_of_features = abs(corr_obj[feature1][feature2]);
                    corr_feature1_with_target = corr_obj[target_feature][feature1]
                    corr_feature2_with_target = corr_obj[target_feature][feature2]

                    if corr_obj[target_feature][feature1] >= corr_obj[target_feature][feature2]:
                        dropFeature.add(feature2);
                        reduced_features[feature2] = explaination_collinear.format(feature1, feature2, corr_of_features, collinear_threshold, target_feature, corr_feature1_with_target, corr_feature2_with_target);
                    else:
                        dropFeature.add(feature1);
                        reduced_features[feature1] = explaination_collinear.format(feature2, feature1, corr_of_features, collinear_threshold, target_feature, corr_feature2_with_target, corr_feature1_with_target);
                        feature1_removed = True;
                j = j + 1;

            for feature1  in dropFeature:
                size_feature = size_feature - 1
                available_features.remove(feature1);
                del corr_obj[feature1];
                for feature2 in corr_obj.keys():
                    del corr_obj[feature2][feature1];

            if feature1_removed == False:
                i = i + 1;
     
    # Remove all features those having less correlation with target variable than correlation threshold
    if corr_threshold != None:
        for feature in corr_obj[target_feature].keys():
            if abs(corr_obj[target_feature][feature]) < corr_threshold:
                reduced_features[feature] = explaination_corr.format(corr_threshold, feature, target_feature, abs(corr_obj[target_feature][feature]));  
                dropFeature.add(feature)
                
        for feature in dropFeature:
            del corr_obj[feature];
            del corr_obj[target_feature][feature];
            available_features.remove(feature);
            size_feature = size_feature - 1;
            
    
    corr_with_target = dict()
    
    for feature1, corr1 in corr_obj[target_feature].items():
        corr_with_target[feature1] = corr1
            
    return reduced_features, corr_with_target;