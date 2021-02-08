from fuzzywuzzy import fuzz
import pandas as pd
import re
import string
from difflib import SequenceMatcher



#read lists, remove floats
list1=pd.read_csv("D:\\fuzzy\\rpro_tap_sub_name.csv")
list2=pd.read_csv("D:\\fuzzy\\db_3_4.csv")

row_remove_1 = list()
row_remove_2 = list()

for i in range(0, len(list1)):
    list1['tap_sub_name'][i] = str(list1['tap_sub_name'][i])
for i in range(0, len(list2)):
    list2['demandbase_company_name'][i] = str(list2['demandbase_company_name'][i])

for j in range(0, len(list1)):
    if type(list1['tap_sub_name'][j]) is not str:
        row_remove_1.append(j)

for k in range(0, len(list2)):
    if type(list2['demandbase_company_name'][k]) is not str:
        row_remove_2.append(k)
        
print(str(len(row_remove_1)) + 'is being removed from list1')
print(str(len(row_remove_2)) + 'is being removed from list2')

list3 = list1.drop(list1.index[row_remove_1])
list4 = list2.drop(list2.index[row_remove_2])
    
#Remove Punctuations
list3['tap_sub_name_original']  = list3['map_tap_sub_name']
list4['demandbase_company_name_original'] = list4['map_demandbase_company_name']
list3['tap_sub_name'] = [''.join(c for c in s if c not in string.punctuation) for s in list3['tap_sub_name'] ]
list4['demandbase_company_name'] = [''.join(c for c in s if c not in string.punctuation) for s in list4['demandbase_company_name'] ]


#define dataframe
product_match_df = pd.DataFrame()
product_list1=list3
product_list2=list4

#fuzzy match lists
product_list=[] #LIST OF ALL THE PRODUCTS
product_ratio_list=[] #FUZZY RATIO BETWEEN PRODUCT AND THE PRODUCT MATCH
product_match_list=[] #PRODUCT MATCH LIST
product_original_list=[]
product_target_list=[]


for each in range(0,len(product_list2['demandbase_company_name'])):
	print ('Doing'+ str(each))
	print('---------------------')
	product_ratio=0
	product=product_list2['demandbase_company_name'][each]
	product_original = product_list2['demandbase_company_name_original'][each]
	product_match=''
        for k in range(0,len(product_list1['tap_sub_name'])):
            x= fuzz.token_sort_ratio(product_list2['demandbase_company_name'][each],product_list1['tap_sub_name'][k])
            product_target = product_list1['tap_sub_name_original'][k]
            if(x>75):
                print product
                print product_list1['tap_sub_name'][k]
                print x
                product_list.append(product)
                product_ratio_list.append(x)
                product_match_list.append(product_list1['tap_sub_name'][k])
                product_original_list.append(product_original)
                product_target_list.append(product_target)
            else :
                continue
                
product_match_df = pd.DataFrame()     
product_match_df['product_name'] = product_list
product_match_df['product_ratio']= product_ratio_list
product_match_df['product_match']= product_match_list
product_match_df['Product_original'] = product_original_list
product_match_df['target_original'] = product_target_list

#product_match_df['Country'] = product_list1['country_code_iso2']
#product_match_df['map_demandbase_company_name'] = product_list2['map_demandbase_company_name']
#product_match_df.columns = ['Product', 'Ratio', 'Product_match']

product_match_df


product_match_df.to_csv("D:\\fuzzy\\STAGE2_RES_DB_3_4.csv")