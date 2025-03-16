
# for identifying the differnce between two stocks
 
df1_not_in_df2 = df1[~df1["DATE"].isin(df2["DATE"])]
print(df1_not_in_df2)

------------------------------------------------------------
