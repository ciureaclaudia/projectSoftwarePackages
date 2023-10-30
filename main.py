import numpy as np
import pandas as pd
from functions import *
import statsmodels.formula.api as smf


df=pd.read_csv("DataIN/mcu_box_office.csv", index_col=0, thousands=',', parse_dates=['release_date'])

#       MINIM 6 din
# -	definirea și apelarea unor funcții;             OK
# -	utilizarea structurilor condiționale;           OK(if)
# -	utilizarea structurilor repetitive;             OK (for)

# -	utilizarea listelor și a dicționarelor, incluzând metode specifice acestora;        OK (dict-items,key / list-append, sorted)
# -	utilizarea seturilor și a tuplurilor, incluzând metode specifice acestora;          !(tuplu)


# ANALIZA: care este diferenta de venituri dintre filmele apreciate mai bine/mai slab de public si experti
scores_tuple=[s for s in zip(df['tomato_meter'], df['audience_score'])]
score_dict,  score_differences = create_scores_dictionary(df, scores_tuple, procent=80)
dict_df=pd.DataFrame(score_dict).transpose()
dict_df.to_csv("DataOUT/movie_scores_dictionary.csv")
print('Scores below 80%', score_differences)

revenue_list_high, revenue_list_low=create_revenue_lists(df, score_differences)
revenue_list_high_formatted = ["{:,.0f}$".format(revenue) for revenue in sorted(revenue_list_high)]
revenue_list_low_formatted = ["{:,.0f}$".format(revenue) for revenue in sorted(revenue_list_low)]
print('Sorted high scores revenues',revenue_list_high_formatted, '\nSorted low scores revenues', revenue_list_low_formatted)
print('High scores revenue mean',np.round(np.mean(revenue_list_high),3), '\tLow scores revenue mean',
      np.round(np.mean(revenue_list_low),3), '\tMean difference', np.round(np.mean(revenue_list_high)-np.mean(revenue_list_low),3))



# -	importul unei fișier csv sau json în pachetul pandas;           OK
# -	accesarea datelor cu loc și iloc;           OK(iloc)
# -	modificarea datelor în pachetul pandas;
# -	utilizarea funcțiilor de grup;              OK(apply)
# -	tratarea valorilor lipsă;

#ANALIZA: clasament filme dupa profitul rezultat
df_rankings_top10 = rank_based_on_column(df, "profit")
df_rankings_top10.to_csv("DataOUT/profit_rankings.csv")


# -	ștergerea de coloane și înregistrări;
# -	prelucrări statistice, gruparea și agregarea datalor în pachetul pandas;        OK(groupby, agg)
# -	prelucrarea seturilor de date cu merge / join;

#ANALIZA: cum s-au modificat investitiile in filme de-a lungul existentei companiei
min_max_mcu_phase = group_min_max(df, 'production_budget', 'mcu_phase')
min_max_mcu_phase.to_csv("DataOUT/min_max_mcu_phase.csv")


# -	reprezentare grafică a datelor cu pachetul matplotlib;          OK(line3, bar2)

#ANALIZA: comparatie scoruri audienta vs scoruri critici
# create_bar_chart_scores(df)
#
# #ANALIZA: comparatie incasari la lansare vs locale vs globale
# create_line_chart_box_office(df)


# -	utilizarea pachetului scikit-learn (clusterizare, regresie logistică)
# -	utilizarea pachetului statmodels (regresie multiplă)                OK(train)

#ANALIZA: influenta scorului audientei si a bugetului productiei asupra incasarii globale
# + predictia incasarilor pe baza modelului de regresie multipla
x = pd.DataFrame(df, columns=['audience_score', 'production_budget'])
y = df['worldwide_box_office']
predictions_df = generate_multiple_regression_model(df, x, y)
predictions_df.to_csv('DataOUT/multiple_regression_predictions.csv')


#ANALIZA: analiza influentei duratei filmului asupra incasarilor din opening weekend
x=df['movie_duration'].values
y=df['opening_weekend'].values

resultss = smf.ols('y ~ x', data=df).fit()
simple_regression_coefficients = resultss.params
print("Simple regression coefficients", simple_regression_coefficients)
print(resultss.summary())
predictions = round(resultss.predict(df), 3)
predictions_dff = pd.DataFrame(predictions)

r2 = r2_score(y, predictions_dff)
mse = mean_squared_error(y, predictions_dff)
print("R-squared:", np.round(r2, 3), "\tMSE:", np.round(mse, 3))

predictions_dff.to_csv('DataOUT/simple_regression_predictions.csv')


#SORTARE: sortare descrescatoare file dupa data aparitiei
df_sort = df.sort_values(by='release_date',ascending=False)
df_sort.to_csv('DataOUT/descending_sort_release_date.csv')

#MODIFICARE SET DATE IN PANDAS: stergere COLOANE audience_score, tomato_meter
# Ștergere coloane (ca listă), salvare într-un nou fișier csv
df_delete = df.drop(["audience_score", "tomato_meter"], axis=1)
print(df_delete.head())
df_delete.to_csv('DataOUT/delete_df.csv', index = False)
