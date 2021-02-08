# importing all requied functions
from selenium import webdriver
import pandas as pd
import time
import re
import numpy as np
import math

#chrome driver path:
driver_path = r'C:/Users/shruti.kamath/Downloads/chromedriver.exe'


#function for extraction
def sql_result_extraction(link):
    browser = webdriver.Chrome(executable_path= driver_path)
    queries_df = pd.DataFrame(columns=['SQL_Test','Q_No','Questions','Name','Answers','link'])
    browser.maximize_window()
    browser.get(link)
    time.sleep(10)  # wait time for the page to load completely

    questions = browser.find_elements_by_xpath("//div[@class ='ui-sm-11 ui-md-11 ui-lg-11 ui-xl-11 question_data']")
    question_number = browser.find_elements_by_xpath("//div[@class ='ui-sm-1 ui-md-1 ui-lg-1 ui-xl-1 question_number']")
    candidate = browser.find_elements_by_xpath("//div[@class ='ui-sm-4 ui-md-4 ui-lg-4 ui-xl-4 analysis_headings']")

    answers = browser.find_elements_by_xpath("//div[@class ='ace_content']")
    answer_list = []

    for x in range(len(answers)):
        js_string = str("return document.getElementsByClassName('ace_content')["+str(x)+"].textContent;")
        ans = browser.execute_script(js_string)
        answer_list.append(ans)
    for x in range(len(answers)):
        ans_list= []
        ans = answer_list[x]
        ans = ans.replace('# You are using MYSQL','')

        for y in ans.split('\n'):
            for z in y.split('\r'):
                z = str(z.split('--')[0].split('/*')[0])
                ans_list.append(z)

        ans = ''.join(ans_list)

        qn_edited = ''.join(questions[x].text.split(' '))

        qn_edited = qn_edited.replace('Note:Thedatasetisalreadypresentinthesystem.','').replace('\n','').replace('\r','') 

        queries_df = queries_df.append({'Questions': qn_edited, 
                                        'Q_No':question_number[x].text,
                                        'Answers': ans,
                                        'Name' : candidate[0].text.split(':')[1],
                                        'SQL_Test' : candidate[2].text.split(':')[1],
                                        'link' : link},
                                        ignore_index = True)
    return queries_df


#SQL evaluation ref no 1
def sql_automation_question_1(test_string):
    marks_question_1=[]
    test_string=str(test_string)
    test_string=test_string.lower()
    test_string=re.sub(' +', ' ', test_string)
    select_position=test_string.find('select')
    from_position=test_string.find('from')
    where_position=test_string.find('where')
    group_position=test_string.find('group')
    
    
    sql_order=[]
    from_clause=[]
    where_clause=[]
    select_clause=[]
    group_by_clause=[]
    calculation=[]
    
    if (select_position<from_position)&(from_position<where_position)&(where_position<group_position):
        sql_order.append(0.5)
    else:
        sql_order.append(0)
        print('improper order of SQL clause')
    if re.search(r'(from|join)[a-z.\s]{0,10}(transaction|shipping)[a-z\s]{0,15}join[a-z.\s]{0,10}(transaction|shipping)[a-z\s]{0,15} on [a-z]{0,15}.shipping_id[\s]{0,1}=[\s]{0,1}[a-z]{0,15}.shipping_id',test_string):
        from_clause.append(1)
    else:
        from_clause.append(0)
        print('from clause1: trasaction- shipping join error')
    if re.search(r'(from|join)[a-z.\s]{0,15}(carrier)[a-z\s]{0,15}(on) [a-z.]{0,15}(carrier_id)(\s){0,1}(=)(\s){0,1}[a-z.]{0,15}(carrier_id)',test_string):
        from_clause.append(1)
    else:
        from_clause.append(0)
        print('from clause2: carrier- shipping join error')
    if re.search(r'(where|and)[^(\|\?|\!)]{0,10}(check_out_status)(\s){0,1}(=)(\s){0,1}(\'1\'|1)',test_string):
        where_clause.append(1)
    else:
        where_clause.append(0)
        print('incorrect filtering for checkout status')
    if re.search(r'(where|and)[^(\|\?|\!)]{0,10}(is_listed)(\s){0,1}(=)(\s){0,1}(\'0\'|0|false|\'no\'|\'n\')',test_string):
        where_clause.append(1)
    else:
        where_clause.append(0)
        print('incorrect filtering for is_listed')
    group_clause=''
    if re.search(r'group by(.*)',re.sub(' +', ' ', test_string.lower())):
        group_clause=re.search(r'group by(.*)',re.sub(' +', ' ', test_string.lower())).group()
    if re.search(r'1|extract\(month from[a-z.\s]{0,10}seller_ship_date\)|month\([a-z.\s]{0,10}seller_ship_date\)|monthname\([a-z.\s]{0,10}seller_ship_date\)',group_clause):
        group_by_clause.append(0.5)
    else:
        group_by_clause.append(0)
        print('shipping month not used in group by')
    selected_elements=''
    if re.search(r'select(.*)from[a-z.\s]{0,10}(transaction|shipping|carrier)',test_string):
        selected_elements=re.search(r'select(.*)from[a-z.\s]{0,10}(transaction|shipping|carrier)',test_string).group()
    if re.search(r'extract[\s]{0,1}\([\s]{0,1}month from[a-z.\s]{0,10}seller_ship_date[\s]{0,1}\)|month[\s]{0,1}\([a-z.]{0,10}seller_ship_date[\s]{0,1}\)|monthname[\s]{0,1}\([a-z.]{0,10}seller_ship_date[\s]{0,1}\)',selected_elements):
        select_clause.append(0.5)
    else:
        select_clause.append(0)
        print('shipping month not in select')
    if re.search(r'sum\([a-z.]{0,10}price(\s){0,1}\*(\s){0,1}[a-z.]{0,10}quantity\)',test_string):
        calculation.append(0.5)
    else:
        calculation.append(0)
        print('transaction amount not calculated properly')
    if re.search(r'from [a-z.]{0,10}transaction[a-z\s]{0,10},[\s]{0,1}shipping',test_string):
        if re.search(r'(where|and)[\s]{0,1}[a-z.]{0,10}shipping_id=[a-z.]{0,10}shipping_id',test_string):
            from_clause.append(1)
    if re.search(r'(where|and)[\s]{0,1}[a-z.]{0,10}carrier_id in \([\s]{0,1}select carrier_id from carrier where is_listed[\s]{0,1}=[\s]{0,1}\'(n|no|0)\'[\s]{0,1}\)',test_string):
        from_clause.append(1)
        where_clause.append(1)
    if re.search(r'(from|join)[a-z.\s]{0,15}(carrier)[a-z\s]{0,15}(on) [a-z.]{0,15}(carrier_id)(\s){0,1}(=)(\s){0,1}[a-z.]{0,15}(carrier_id)',test_string):
        from_clause.append(1)
    else:
        from_clause.append(0)
    if re.search(r'(from|join)[a-z.\s]{0,15}carrier using \([\s]{0,1}carrier_id',test_string):
        from_clause.append(1)
    else:
        from_clause.append(0)
    if re.search(r'(from|join)[a-z.\s]{0,15}shipping using \([\s]{0,1}shipping_id',test_string):
        from_clause.append(1)
    else:
        from_clause.append(0)
    sql_order=sum(sql_order)
    from_clause=sum(from_clause)
    where_clause=sum(where_clause)
    select_clause=sum(select_clause)
    group_by_clause=sum(group_by_clause)
    calculation=sum(calculation)
    
    sql_order= 0.5 if sql_order > 0.5 else sql_order
    from_clause= 2 if from_clause > 2 else from_clause
    where_clause= 2 if where_clause > 2 else where_clause
    select_clause= 0.5 if select_clause > 0.5 else select_clause
    group_by_clause= 0.5 if group_by_clause > 0.5 else group_by_clause
    calculation= 0.5 if calculation > 0.5 else calculation
    
    marks_question_1=sql_order+from_clause+where_clause+select_clause+group_by_clause+calculation
    return(marks_question_1)

# function for SQL Evaluation Ref no 2
def sql_automation_question_2(string):
    marks_question_2=[]
    total_marks=[]
    string=str(string)
    ##We don't need any joins in this questiom
    ##if re.search(r'( on)[^(\|\?|\!)]{0,6}(seller_id)',string):
    ##    if re.search(r'(=)[^(\|\?|\!)]{0,6}(seller_id)',string):
    ##        marks_question_2.append(1)
    ##else:
    ##    marks_question_2.append(0)
        
    ##if re.search(r'(where)[^(\|\?|\!)]{0,6}(seller_id)',string):
    ##    if re.search(r'(=)[^(\|\?|\!)]{0,6}(seller_id)',string):
    ##        marks_question_2.append(1)
    ##else:
    ##    marks_question_2.append(0)
        
    
    ## from transaction table alone we need output -1
    if re.search(r'(from)[^(\|\?|\!)]{0,}(transaction)',string):
        marks_question_2.append(1.0)
    else:
        marks_question_2.append(0)
        
    ##if re.search(r'(join)[^(\|\?|\!)]{0,1}(transaction|seller)',string):
    ##    marks_question_2.append(0.5)
    ##else:
    ##    marks_question_2.append(0)
    
    ## Values for getting top n -1
    if re.search(r'(order by )[^\|\?|\!]{0,1}(sales|total_Sales)',string) | re.search((r'(order by )[^\|\?|\!]{0,1}(sum)[^\|\?|\!]{0,}(quantity)',string) && (r'(order by )[^\|\?|\!]{0,1}(sum)[^\|\?|\!]{0,}(price)',string) ):
        if re.search(r'(order by )[^(\|\?|\!)]{0,20}(desc)',string):
            marks_question_2.append(1.0)
    else:
        marks_question_2.append(0)
    
    ## Top n check -1
    if re.search(r'(limit)[^(\|\?|\!)]{0,1}(10)',string):
        marks_question_2.append(1.0)
    else:
        marks_question_2.append(0)
    
    if re.search(r'(top)[^(\|\?|\!)]{0,1}(10)',string):
        marks_question_2.append(1.0)
    else:
        marks_question_2.append(0)
    
    ##Column to be considered for top n -1
    if re.search(r'(select)[^(\|\?|\!)]{0,3}(name|seller_id|1|2)',string):
        marks_question_2.append(1)
    else:
        marks_question_2.append(0)
    
    ## Group by statement -1
    if re.search(r'(group by)[^(\|\?|\!)]{0,10}(name|seller_id|1|2)',string):
        marks_question_2.append(1)
    else:
        marks_question_2.append(0)
    
    ## Date filter -1
    if re.search(r'(where)[^\|\?|\!]{0,100}(transaction_date)',string):
        marks_question_2.append(0.5)
    else:
        marks_question_2.append(0)
    
    if re.search(r'(where)[^\|\?|\!]{0,100}(2015)',string):
        marks_question_2.append(0.5)
    else:
        marks_question_2.append(0)
    
    ##total_marks.append(sum(marks_question_2))
    return(sum(marks_question_2))

#function for SQL ref no 3

def sql_automation_question_3(string):
    marks_question_3=[]
    string=str(string)
    ## Join between 
    ##if re.search(r'\s(on|where)[^(\|\?|\!)]{0,}(object_id|buyer_id|site_id)',string):
    ##    if re.search(r'(=)[^(\|\?|\!)]{0,10}(object_id|buyer_id|site_id)',string):
    ##        marks_question_3.append(0.5)
    ##else:
    ##    marks_question_3.append(0)
    
    ## From Table 0.5 
    if re.search(r'(from)[^(\|\?|\!)]{0,}(transaction )',string):
        marks_question_3.append(0.5)
    else:
        marks_question_3.append(0)
    
    ## Table 2 0.5
    if re.search(r'(join|from)[^(\|\?|\!)]{0,}(category )',string):
        marks_question_3.append(0.5)
    else:
        marks_question_3.append(0)
        
    ## join criteria 1
    if re.search(r'\s(on|where)[^(\|\?|\!)]{0,80}(site_id|leaf_category_id)',string):
        if re.search(r'(=)[^(\|\?|\!)]{0,10}(leaf_category_id)',string) and re.search(r'(=)[^(\|\?|\!)]{0,10}(site_id)',string):
            marks_question_3.append(1.0)
    else:
        marks_question_3.append(0)
        
        
    if re.search(r'\s(on|where)[^(\|\?|\!)]{0,80}(site_id|leaf_category_id)',string):
        if re.search(r'( in)\s\((select)\s(site_id|leaf_category_id)',string):
            marks_question_3.append(1.0)
    else:
        marks_question_3.append(0)
    
    ## Column to be considered 1.0
    
    if re.search(r'(select)[^\|\?|\!]{0,10}(object_id)',string):
        marks_question_3.append(0.5)
    else:
        marks_question_3.append(0)
    
    if re.search(r'(select)[^\|\?|\!]{0,50}(count)[^\|\?|\!]{0,50}(buyer))',string):
        marks_question_3.append(0.5)
        
    else:
        marks_question_3.append(0)

    ## Limit/Max/top n    -1
    if re.search(r'(order by)[^\|\?|\!]{0,10}(bcount|buyer_count|object_id|1|2)',string):
        if re.search(r'(order by )[^(\|\?|\!)]{0,20}(desc)',string):
            marks_question_3.append(0.5)
    else:
        marks_question_3.append(0)
        
    if re.search(r'(limit)[^(\|\?|\!)]{0,10}(1)',string):
        marks_question_3.append(0.5)
    else:
        marks_question_3.append(0)
        
    if re.search(r'( top)[^(\|\?|\!)]{0,10}(1)',string):
        marks_question_3.append(0.5)
    else:
        marks_question_3.append(0)  
        
    if re.search(r'(max)[^\|\?|\!]{0,10}(buyer)',string):
        marks_question_3.append(1.0)
        
    else:
        marks_question_3.append(0)

    ## Group by criteria 1
    if re.search(r'(group by)[^(\|\?|\!)]{0,10}(item|object_id|1|2)',string):
        marks_question_3.append(0.5)
    else:
        marks_question_3.append(0)
    
    ##Fashion Filter 1
    if re.search(r'(where)[^\|\?|\!]{0,}(vertical)',string):
        if re.search(r'(vertical)[^\|\?|\!]{0,10}(fashion)',string):
            marks_question_3.append(1.0)
    else:
        marks_question_3.append(0)
        
    return(sum(marks_question_3))

##

#SQL evalation function for ref no 4

def sql_automation_question_4(string):
    marks_question_4=[]
    criteria_1=[]
    criteria_2=[]
    criteria_3=[]
    Base_criteria=[]
    criteria_4=[]
    criteria_5=[]
    criteria_6=[]
    
    ## 1st level check: For Table and join-2 , unless this is met no point scoring further.
         
    if re.search(r'(from)[^(\|\?|\!)]{0,}(seller)',string):
        criteria_1.append(0.25)
    else:
        criteria_1.append(0)

    if re.search(r'(from)[^(\|\?|\!)]{0,}(transaction)',string):
        criteria_1.append(0.25)
    else:
        criteria_1.append(0)
        
    if sum(criteria_1)==0.5 and re.search(r'(join)[^(\|\?|\!)]{0,1}(transaction|seller)',string):
        criteria_2.append(0.5)
    else:
        criteria_2.append(0)
        
        
    if re.search(r'( on)[^(\|\?|\!)]{0,12}(seller_id)',string):
        if re.search(r'(=)[^(\|\?|\!)]{0,12}(seller_id)',string):
            criteria_3.append(1)
    else:
        criteria_3.append(0)
                     
    if sum(criteria_3)==0 and re.search(r'(where)[^(\|\?|\!)]{0,12}(seller_id)',string):
        if re.search(r'(=)[^(\|\?|\!)]{0,12}(seller_id)',string):
            criteria_3.append(1)
    else:
        criteria_3.append(0)
 
    if sum(criteria_3)==0 and re.search(r'(where)[^(\|\?|\!)]{0,12}(seller_id)',string):
        if re.search(r'(in)\s\([^(\|\?|\!)]{0,12}(seller_id)',string):
            criteria_3.append(1)
    else:
        criteria_3.append(0)
        
    Base_criteria= sum(criteria_1)+sum(criteria_2)+sum(criteria_3)  
    
    ##For identifying Country filter.-1
    
    
    if re.search(r'(country)[^\|\?|\!]{0,10}(china)',string):
        criteria_4.append(1.0)
    else:
        criteria_4.append(0)

    ## For identifying Date Filter    -1
    if  re.search(r'(where)[^\|\?|\!]{0,}(2015)',string):
        criteria_5.append(0.5)
    else:
        criteria_5.append(0)    
        
    
    if re.search(r'(where)[^\|\?|\!]{0,}(2015)',string):
        if re.search(r'(2)[^123|\|\?|\!]{0,10}(2015)',string):
            criteria_5.append(0.5)
    else:
        criteria_5.append(0)   
        
    
    if sum(criteria_5)==0.5 and re.search(r'(month)[^\|\?|\!]{0,20}(transaction_date)',string):
        if re.search(r'(month)[^\|\?|\!]{0,40}(2)',string):
            criteria_5.append(0.5)
    else:
        criteria_5.append(0)    
           
    if re.search(r'[^abc\_](count)[^\|\?|\!]{0,20}(seller|1|2)',string):
        criteria_6.append(0.5)
    else:
        criteria_6.append(0)
    
    if re.search(r'(where|case)[^(\|\?|\!)]{0,100}(week|datediff)',string):
        criteria_6.append(1)
        
    else:
        criteria_6.append(0)    
        
                     
    if re.search(r'(group by)[^(\|\?|\!)]{0,10}(week|1|2|seller_id)',string):
        criteria_6.append(0.5)
    else:
        criteria_6.append(0)    
    
    marks_question_4=Base_criteria+sum(criteria_5)+sum(criteria_4)+sum(criteria_6)
    return(marks_question_4)

#SQL evaluation for ref no 5

def sql_automation_question_5(string):
    
    marks_question_5=[]
    total_marks=[]
    criteria_1=[]
    criteria_3=[]
    
    ##TABLES -1 
    if re.search(r'(from)[^(\|\?|\!)]{0,}(transaction )',string):
        criteria_1.append(0.5)
    else:
        criteria_1.append(0)
        
    if re.search(r'(from)[^(\|\?|\!)]{0,}(shipping )',string):
        criteria_1.append(0.5)
    else:
        criteria_1.append(0)    
    
    ##JOINS 1
       
    if re.search(r'( on)[^(\|\?|\!)]{0,12}(shipping_id)',string):
        if re.search(r'(=)[^(\|\?|\!)]{0,12}(shipping_id)',string):
            criteria_3.append(1.0)
    else:
        criteria_3.append(0)
                     
    if sum(criteria_3)==0 and re.search(r'(where)[^(\|\?|\!)]{0,12}(shipping_id)',string):
        if re.search(r'(=)[^(\|\?|\!)]{0,12}(shipping_id)',string):
            criteria_3.append(1.0)
    else:
        criteria_3.append(0)
 
    if sum(criteria_3)==0 and re.search(r'(where)[^(\|\?|\!)]{0,12}(shipping_id)',string):
        if re.search(r'(in)\s\([^(\|\?|\!)]{0,12}(shipping_id)',string):
            criteria_3.append(1)
    else:
        criteria_3.append(0)
     
    ## cOUNT -2
    if re.search(r'(select)[^(\|\?|\!)]{0,3}(count)',string):
    #if re.search(r'[^(\|\?|\!)]{0,3}(distinct)',string):
        if re.search(r'[^(\|\?|\!)]{0,3}(transaction_id)',string):
            marks_question_5.append(2)
    else:
        marks_question_5.append(0)
    
    ## tiME 2
    if re.search(r'(where)[^\|\?|\!]{0,100}(seller_ship_timestamp|delivery_timestamp)',string):
        if re.search(r'[^\|\?|\!]{0,100}(11|11:00|2300|23)',string):
            if re.search(r'[^\|\?|\!]{0,100}(2|2:00|0200|02|1|1:00|0100|01)',string):
                marks_question_5.append(2)
    else:
        marks_question_5.append(0)
 
    return (sum(marks_question_5)+sum(criteria_1)+sum(criteria_3) )


#master evaluation function
def sql_evaluation(df):
    if df['ref_no']==1:
        return(sql_automation_question_1(df['Answers']))
    if df['ref_no']==2:
        return(sql_automation_question_2(df['Answers']))
    if df['ref_no']==3:
        return(sql_automation_question_3(df['Answers']))
    if df['ref_no']==4:
        return(sql_automation_question_4(df['Answers']))
    if df['ref_no']==5:
        return(sql_automation_question_5(df['Answers']))
        
def score_extraction(links):
    # questions to refernce number mapping
    question_1="From the given ER diagram representing the database schema, write a MySQL query to do the following operation:Calculate Total Transaction Amount (Price * Quantity) for confirmed transactions (check_out_status = 1) that get shipped by unlisted carriers at a shipping month level."
    question_2="From the given ER diagram representing the database schema, write a MySQL query to do the following operation:Find the top 10 of the sellers based on their sales in 2015"
    question_3="From the following ER diagram representing the database schema, write a MySQL query to find the item(object_id) with maximum number of buyers in fashion vertical.Display item and buyer countsNote:Thedatasetisalreadypresentinthedatabase"
    question_4="From the given ER diagram representing the database schema, write a MySQL query to do the following operation:Find the number of sellers from China who have transacted atleast once in every week during the month of February 2015"
    question_5="From the given ER diagram representing the database schema, write a MySQL query to do the following operation:Provide the number of transactions with wrong shipping timestamp. There are shipments that have shipping timestamp (varchar format) around midnight (11pm to 2am). Those are considered to be wrong updates. "
    
    # trimming the spaces in questios for mapping:
    question_1=re.sub('\s',"",question_1)
    question_2=re.sub('\s',"",question_2)
    question_3=re.sub('\s',"",question_3)
    question_4=re.sub('\s',"",question_4)
    question_5=re.sub('\s',"",question_5)
    
    # final question mapping data frame:
    question_df=pd.DataFrame([{"question":question_1,"ref_no":1},{"question":question_2,"ref_no":2},{"question":question_3,"ref_no":3},{"question":question_4,"ref_no":4},{"question":question_5,"ref_no":5}])
    
    #data frame of all the extracted content
    queries_df=pd.concat([sql_result_extraction(i) for i in links])
    #Score the extracted results 
    result_df=queries_df.merge(question_df,how='inner',left_on="Questions",right_on="question")
    result_df['script_score']=result_df.apply(lambda x: sql_evaluation(x),axis=1)
    result_df['adjusted_script_score']=result_df['script_score']*10/6
    mapping_df=result_df[['Name','link']].drop_duplicates()
    result_df=result_df.pivot(index='link', columns='Q_No', values='script_score').reset_index()
    result_df['Total']=result_df['1']+result_df['2']+result_df['3']+result_df['4']+result_df['5']
    result_df=result_df.merge(mapping_df)[['Name','link','1','2','3','4','5','Total']]
    result_df["result"] = result_df["Total"].apply(lambda x: "pass" if x>17 else "manual" if x>11 else "fail")
    return result_df