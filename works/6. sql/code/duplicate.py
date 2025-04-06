"""
数据来源: https://blog.csdn.net/qq_52213943/article/details/124496420
"""
import pandas as pd
df =pd.read_csv(r'works\6. sql\others\source_data.csv', encoding='gbk', dtype=str)
# 按照第一列去重，并且删去空值
df = df.drop_duplicates(subset=['小类编码']).dropna(subset=['小类编码'])
df.to_csv(r'works\6. sql\others\data.txt',index=False,header=False,sep=',')

