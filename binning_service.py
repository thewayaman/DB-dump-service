import pandas as pd
import numpy as np

# import seaborn as sns


def createDataFrameFromCSV(file_path):
    return pd.read_csv(file_path)


def savePlot(dataFrameKey, fileName):
    dataFrameKey.plot(kind="hist").get_figure().savefig(fileName)


# weeklyData = createDataFrameFromCSV("./weeklyniftydata.csv")
dailyData = createDataFrameFromCSV("./day_breakup_nifty.csv")

dateWisePricesList = []
for x in dailyData.sample(5).iterrows():
    print(x[1]['day_of_the_week'],x[1]['day_of_the_week'].strip() == "THURSDAY")
print([x for x in dateWisePricesList])

# pd.cut(weeklyData["percentage_change"], bins=20).value_counts(sort=False).plot.bar(
#     rot=0, color="b"
# ).get_figure().savefig("test_fig03.pdf")


# print(
#     pd.cut(weeklyData["percentage_change"], bins=16).value_counts(),
#     pd.cut(dailyData["percentage_change"], bins=16).value_counts(),
# )
# savePlot(weeklyData['percentage_change'],'test_fig0.pdf')
# savePlot(dailyData['percentage_change'],'test_fig1.pdf')



