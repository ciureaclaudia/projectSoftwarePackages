import numpy as np
import pandas as pd
import matplotlib.pyplot  as plt
import statsmodels.formula.api as smf
from sklearn.metrics import r2_score, mean_squared_error

def create_scores_dictionary(df, tuple, procent):
    score_dict = {}
    for i, key in enumerate(df.index):
        score_dict[key] = tuple[i]
    score_differences = {key: value for key, value in score_dict.items() if value[0] <procent or value[1] < procent}
    return score_dict, score_differences

def create_revenue_lists(df, dict):
    revenue_list_high = list()
    revenue_list_low = list()
    score_dict_titles = list(dict.keys())
    for title, revenue in zip(df.index, df['worldwide_box_office']):
        if title in score_dict_titles:
            revenue_list_low.append(revenue)
        else:
            revenue_list_high.append(revenue)
    return revenue_list_high, revenue_list_low

def calculate_profit(row):
    return row['worldwide_box_office'] - row['production_budget']

def rank_based_on_column(df, column):
    df[column] = df.apply(calculate_profit, axis=1)
    rank_column=column+'_rank'
    df[rank_column] = df[column].rank(ascending=False).astype(int)
    df_rankings = pd.DataFrame(df[['production_budget', 'worldwide_box_office', column, rank_column]],
                               index=df.index)
    df_rankings_top10 = df_rankings.sort_values('profit_rank').iloc[0:10]
    return df_rankings_top10

def group_min_max(df, agg_column, group_column):
    df_grouped = df[[agg_column, group_column]].groupby(by=group_column)
    df_min_max = df_grouped.agg(budget_MIN=(agg_column, np.min),
                                budget_MAX=(agg_column, np.max))
    return df_min_max

def create_bar_chart_scores(df):
    fig, ax = plt.subplots()
    ax.set_title("Audience VS Critic Scores")
    tomato_bar = ax.bar(np.arange(len(df)) + 0.1, df['tomato_meter'], width=0.4, color='g', label='Tomato Meter')
    audience_bar = ax.bar(np.arange(len(df)) + 0.5, df['audience_score'], width=0.4, color='b', label='Audience Score')
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['release_date'].dt.strftime('%Y'))
    ax.set_xlabel('Years')
    ax.set_ylabel('Score')
    ax.legend(handles=[tomato_bar, audience_bar])
    plt.show()

def create_line_chart_box_office(df):
    fig = plt.figure(figsize=(9, 6))
    ax = fig.subplots(1, 3, sharey=True)
    ax[2]=create_line(df, 'worldwide_box_office', 'Worldwide Box Office', 'y', 'r', ax[2])
    ax[1] = create_line(df, 'domestic_box_office', 'Domestic Box Office', 'b', 'g', ax[1])
    ax[0] = create_line(df, 'opening_weekend', 'Opening Weekend', 'c', 'm', ax[0])
    plt.show()

#ymax = df[['worldwide_box_office', 'domestic_box_office', 'opening_weekend']].max()
    # for i in range(len(ax)):
    #     ax[i].set_ylim([0, ymax[i]])

def create_line(df, column, subtitle, c1, c2, ax):
    ax.plot(df['release_date'], df[column], label=column, color=c1)
    ax.set_title(subtitle)
    for i in range(len(df)):
        ax.scatter(df['release_date'][i], df[column][i], c=c2)
        ax.annotate(df.index[i], (df['release_date'][i], df[column][i]), xytext=(5, 5),
                       textcoords='offset points', fontsize=8)
    ax.set_xlabel('Years')
    ax.set_ylabel('Revenue')
    return ax

def generate_multiple_regression_model(df, x, y):
    results = smf.ols('y ~ x', data=df).fit()

    multiple_regression_coefficients = results.params
    print("Multiple regression coefficients", multiple_regression_coefficients)
    print(results.summary())
    predictions = round(results.predict(df), 3)
    predictions_df = pd.DataFrame(predictions)

    r2 = r2_score(y, predictions_df)
    mse = mean_squared_error(y, predictions_df)
    print("R-squared:", np.round(r2, 3), "\tMSE:", np.round(mse,3))

    return predictions_df

