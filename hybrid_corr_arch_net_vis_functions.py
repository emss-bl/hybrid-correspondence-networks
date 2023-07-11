#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 09:18:21 2023

@author: personaldigitalarchives
"""
#import modules
import mailbox
import csv
import pandas as pd
import numpy as np
from pandas import *
import re
from bs4 import BeautifulSoup
import geoip2.database
import spacy
spacy.load('en_core_web_lg')
nlp = spacy.load("en_core_web_lg")
 
#mbox to gephi extractor function for e-mail only   
def extract_mbox_metadata(mbox_file_path):
    #variables
    body = None
    entity_index=0
    #list intialisation
    extracted_email_sender_address_list=[]
    extracted_email_receiver_address_list=[]
    date_list=[]
    clean_date_list=[]
    initial_email_sender_name_list=[]
    initial_email_receiver_name_list=[]
    email_sender_name_list=[]
    email_receiver_name_list=[]
    sender_email_address_list=[]
    receiver_email_address_list=[]
    body_list=[]
    clean_body_list=[]
    ip_list=[]
    digital_sender_lat_list=[]
    digital_sender_long_list=[]
    work_of_art_entity_list=[]
    my_file=open("bibliography.txt", "r")
    data=my_file.read()
    authour_works_checklist=data.split(",")
    my_file.close()
    new_entity_list=[]
    name_of_gdpr_file=input("Name your collection, this will be used for output files...")
    #extracts mbox data to lists
    for message in mailbox.mbox(mbox_file_path):
        extracted_email_sender_address_list.append(message['from'])
        extracted_email_receiver_address_list.append(message['to'])
        date_list.append(message['date'])
    #removes six final characters to make UTC Code
    for item in date_list:
        clean_date_list.append(item[:-6])
   #extracts email addresses and proper names from sender names
    for item in extracted_email_sender_address_list:
       match = re.sub(r'[\w\.-]+@[\w\.-]+',"", str(item))
       regex = re.compile('[^a-zA-Z ]')
       initial_email_sender_name_list.append(regex.sub('', match))
    for item in extracted_email_receiver_address_list:
       match = re.sub(r'[\w\.-]+@[\w\.-]+',"", str(item))
       regex = re.compile('[^a-zA-Z ]')
       initial_email_receiver_name_list.append(regex.sub('', match))
    for item in initial_email_sender_name_list:
       stripped_item = item.strip()
       email_sender_name_list.append(stripped_item)
    for item in initial_email_receiver_name_list:
       stripped_item = item.strip()
       email_receiver_name_list.append(stripped_item)
    for item in extracted_email_sender_address_list:
       match = re.findall(r'[\w\.-]+@[\w\.-]+', str(item))
       sender_email_address_list.append(match)
    for item in extracted_email_receiver_address_list:
       match = re.findall(r'[\w\.-]+@[\w\.-]+', str(item))
       receiver_email_address_list.append(match)
    #Appends message body to list
    for message in mailbox.mbox(mbox_file_path):
        if message.is_multipart():
            for part in message.walk():
                if part.is_multipart():
                    for subpart in part.walk():
                        if subpart.get_content_type() == 'text/plain':
                            body = subpart.get_payload(decode=True)
                        elif part.get_content_type() == 'text/plain':
                            body = part.get_payload(decode=True)
                        elif message.get_content_type() == 'text/plain':
                            body = message.get_payload(decode=True)
        body_list.append(body)
        #Strips formatting from email body
    for item in body_list:
        if item != None:
            clean_body_list.append(BeautifulSoup(item, "lxml").text)
        else:
            clean_body_list.append('No Message Body Found')
    print('Initial metadata extraction complete')
    user_geolocate=input("Would you like to geocode the IP addresses in this collection? Y or N?")
    if user_geolocate=="Y":
    #Searches through message headers for ip addresses, exclusing local loop-back address which is self-referential
        for message in mailbox.mbox(mbox_file_path):
            mbytes=message.as_bytes()
            clean_string=mbytes.decode('utf-8', errors ='replace')
            replaced_string = clean_string.replace('127.0.0.1', 'LOOPBACK')
            replaced_string2=replaced_string.replace('10.0.1.2', 'PRIVATE')
            Result = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', replaced_string2)
            if Result:
                ip_list.append(Result.group())
            else:
                ip_list.append('')
    #Checks IP Addresses against MaxMind Databas
        with geoip2.database.Reader('GeoIP2-City.mmdb') as reader:
            for item in ip_list:
                if item != '':
                    response = reader.city(item)
                    digital_sender_lat_list.append(response.location.latitude)
                    digital_sender_long_list.append(response.location.longitude)
                else:
                    digital_sender_long_list.append('')
                    digital_sender_lat_list.append('')
        print('IP Geolocation Complete')
    else:
        if user_geolocate=="N":
            for item in email_sender_name_list:
                digital_sender_long_list.append('')
                digital_sender_lat_list.append('')
        print('IP Geolocation Skipped')
    user_nlp=input("Would you like to use Natural Language Processing to extract Works of Art from the body of the e-mails in this collection? This process requires a correctly formatted text document at 'bibliography.txt' Y or N?")
    #Uses NLP module to find work of art location to then compare to bibliography.
    if user_nlp=="Y":
        for item in clean_body_list:
            doc = nlp(item)
            inner_work_of_art_list=[]
            for ent in doc.ents:
                if ent.label_=='WORK_OF_ART':
                    inner_work_of_art_list.append(ent.text)
            work_of_art_entity_list.append(inner_work_of_art_list)
        for item in work_of_art_entity_list:
            new_entity_list.append(item)
            entity_index+=1
            if entity_index == len(extracted_email_sender_address_list):
                break
    if user_nlp == "N":
        for item in extracted_email_sender_address_list:
            new_entity_list.append('No NLP Search')
    #Formats works of art correctly in single cell in pandas dataframe and outputs formatted works of art to new list
    raw_mbox_dict = {'Sender Name':email_sender_name_list, 'Receiver Name':email_receiver_name_list,'Date Sent':clean_date_list,'Latitude':digital_sender_lat_list, 'Longitude':digital_sender_long_list, 'Authour Works Raw': new_entity_list}
    mbox_df=pd.DataFrame(raw_mbox_dict)
    mbox_df['Authour Works Raw'] = mbox_df['Authour Works Raw'].astype('string')
    mbox_df2 = mbox_df['Authour Works Raw'].str.split(', ', expand=True)
    for column in mbox_df2:
        mbox_df2[column] = mbox_df2[column].str.replace('[^\w\s]','')
    mbox_df3=mbox_df2[mbox_df2.isin(authour_works_checklist)]
    mbox_df4=mbox_df3.dropna(axis='columns', how='all')
    mbox_df4 = mbox_df4.astype(str)
    mbox_df4 = mbox_df4.replace('<NA>', '')
    mbox_df4['Works by Authour Mentioned in Body'] = mbox_df4[[x for x in mbox_df4.columns]].apply(lambda x: ', '.join(x), axis = 1)
    works_mentioned_list = mbox_df4['Works by Authour Mentioned in Body'].tolist()
    mbox_df_final=mbox_df.drop(columns=['Authour Works Raw'])
    mbox_df_final["Works by Authour Mentioned in Body"] = works_mentioned_list
    mbox_df_final['Date Sent'] = mbox_df_final['Date Sent'].astype(str)
    user_gdpr=input('Would you like to generate a GDPR compliant csv file from your MBOX collection? Y or N?')
    if user_gdpr == "Y":
        mbox_df_final.to_csv(name_of_gdpr_file + ' GDPR Complete Set.csv')
        print('File created')
    if user_gdpr == "N":
        print('File not created')
    user_gephi_outputs=input('Would you like to generate Gephi compliant Node and Edge sheets? Y or N?')
    if user_gephi_outputs == "N":
        print('Program terminated. Thank you!')
        exit()
    if user_gephi_outputs == "Y":
        lat_long_dict=zip(digital_sender_lat_list, digital_sender_long_list)
        lat_long_list=[]
        total_sender_receiver_name_list=email_sender_name_list+email_receiver_name_list
        for x,y in lat_long_dict:
            lat = str(x)
            long = str(y)
            latlong= lat + ',' + long
            lat_long_list.append(latlong)
    #Zips location data and name data to dictionary
        location_dict=dict(zip(total_sender_receiver_name_list, lat_long_list))
    #Creates unique list of nodes for nodes sheet
        node_list=[]
        for item in email_sender_name_list:
            if item not in node_list:
                node_list.append(item)
        node_location_list=[]
        for item in node_list:
            for k,v in location_dict.items():
                if item == k:
                    node_location_list.append(v)
        for item in email_receiver_name_list:
            if item not in node_list:
                node_list.append(item)
                node_location_list.append('No Location Found')
        id_count=0
        id_list=[]
        for item in node_list:
            id_count+=1
            id_list.append(id_count)
        #Labels fields for nodes csv
        node_list.insert(0, 'name')
        node_location_list.insert(0, 'location (long,lat)')
        id_list.insert(0, 'Id')
        #Zips final node dictionary together
        node_dict = zip(id_list, node_list, node_location_list)
        node_dict_without_location = dict(zip(id_list, node_list))
        #Writes nodes dictionary to csv
        with open(name_of_gdpr_file + ' NODE_SHEET.csv', 'w+', encoding='utf-8',newline='' ) as myfile: #writes to new .csv file
            wr = csv.writer(myfile, delimiter=',')
            wr.writerows(node_dict)
        source_list=[]
        target_list=[]
        for item in email_sender_name_list:
            for key, value in node_dict_without_location.items():
                if item == value:
                    source_list.append(key)
        for item in email_receiver_name_list:
            for key, value in node_dict_without_location.items():
                if item == value:
                    target_list.append(key)
            type_list=[]
        for item in email_sender_name_list:
            type_list.append('Digital')
        mbox_df_final.insert(0, "Source", source_list)
        mbox_df_final.insert(1, "Target", target_list)
        mbox_df_final.insert(7, "Type(Phys/Dig)", type_list)
        user_drop_records=input("Do you wish to drop blank records? This is recommended when using these sheets in Gephi. Y or N?")
        if user_drop_records=="Y":
            mbox_df_final_nan=mbox_df_final.mask(mbox_df_final=='')
            mbox_df_final_dropped=mbox_df_final_nan.dropna(subset=['Sender Name','Receiver Name','Date Sent'])
            mbox_df_final_dropped['Date Sent'] = mbox_df_final_dropped['Date Sent'].astype(str)
            mbox_df_final_dropped=mbox_df_final_dropped.loc[(mbox_df_final_dropped['Date Sent'].str.len() == 24) | (mbox_df_final_dropped['Date Sent'].str.len() == 25)]
            new_sender_count_list = mbox_df_final_dropped['Source'].tolist()
            new_sender_count=0
            old_sender_count=0
            for item in new_sender_count_list:
                new_sender_count+=1
            for item in extracted_email_sender_address_list:
                old_sender_count+=1
            sender_difference = old_sender_count - new_sender_count
            print('Dropped', sender_difference, 'incomplete records out of', old_sender_count, 'total records.')
            return mbox_df_final_dropped.to_csv(name_of_gdpr_file + 'EDGES SHEET.csv')
        else:
            print('All records retained. They will require manual cleaning.')
            return mbox_df_final.to_csv(name_of_gdpr_file + ' EDGES SHEET.csv')
        

extract_mbox_metadata('File Path to your MBOX File goes here...')
