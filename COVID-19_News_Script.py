### This program compiles global information about the Coronavirus pandemic and sends an email update to subscribers

## IMPORTS
import sys
import os
import subprocess

from urllib.request import urlopen, Request
from selenium import webdriver

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from datetime import datetime, date
import time

import re
from base64 import b64decode



## SCRAPE SITES FOR DATA/NEWS

def scrape_google():
    htmlOutput = "<h2>Top Stories from Google</h2>"
    textOutput = "\nTop Stories from Google:\nhttps://www.google.com/search?q=COVID-19"

    # Top Stories from Google
    url = "https://www.google.com/search?q=COVID-19"
    driver = webdriver.Chrome()
    driver.get(url)

    top3stories = driver.find_elements_by_class_name("So9e7d")[:3]

    htmlOutput += "<br><div style='display:flex;'>"
    for entry in top3stories:
        raw_html = entry.get_attribute("outerHTML")
        htmlOutput += "<div style='margin-right:25px;'>" + raw_html + "</div>"
    htmlOutput += "</div><br>"
    driver.quit()

    # Link to Google Map Dashboard
    htmlOutput += "<br><h3>View Google's <a href='https://google.com/covid19-map/?hl=en'>Global COVID-19 Map</a></h3>"
    textOutput += "\n\nView Google's Global COVID-19 Map:\nhttps://google.com/covid19-map/?hl=en\n"

    # Global Stats from Google
    htmlOutput += "<h3>Global Statistics from Google</h3>"
    textOutput += "\nGlobal Statistics from Google\nhttps://google.com/covid19-map/?hl=en"

    url = "https://google.com/covid19-map/?hl=en"
    driver = webdriver.Chrome()
    driver.get(url)

    statselement = driver.find_elements_by_class_name("VOxXkf")[1]
    statshtml = statselement.get_attribute("outerHTML")
    htmlOutput += "<br><div style='width:650px;height:300px;overflow:auto;'>" + statshtml + "</div><br>"

    driver.quit()
    return htmlOutput, textOutput



def scrape_bbc():
    htmlOutput = "<br><h2>BBC News Updates</h2></br>"
    textOutput = "\n\n\nBBC News:\n"

    url = "https://bbc.co.uk/search?q=covid-19"
    driver = webdriver.Chrome()
    driver.get(url)

    top3stories = driver.find_elements_by_class_name("ett16tt11")[:3]

    htmlOutput += "<br><div style='display:flex;'>"
    for entry in top3stories:
        headline = entry.find_elements_by_class_name("css-1aofmbn-PromoHeadline")[0]
        headlineLink = headline.find_elements_by_tag_name("a")[0].get_attribute("href")
        headlineText = headline.text
        description = entry.find_elements_by_tag_name("p")[1].text
        imgLink = entry.find_elements_by_tag_name("img")[0].get_attribute("src")
        articleDate = entry.find_elements_by_class_name("css-1hizfh0-MetadataSnippet")[0].text
        if not re.search(r'\d+\s\w+\s\d+', articleDate):
            articleDate = "No date listed"
            
        htmlOutput += "<div style='width:250px;margin-right:25px;'><a href='{1}'><img style='max-width:250px;margin-right:30px;' src='{4}'></a><a href='{1}'><h3>{0}</h3></a><p>{2}</p><p><i>{3}</i></p></div>".format(headlineText, headlineLink, description, articleDate, imgLink)
        textOutput += "\nHeadline: {0}\nDescription: {1}\nDate: {2}\nLink: {3}".format(headlineText, description, articleDate, headlineLink)
    htmlOutput += "</div><br>"

    driver.quit()
    return htmlOutput, textOutput



def scrape_washingtonpost():
    htmlOutput = "<br><h2>Washington Post <a href='https://washingtonpost.com/coronavirus/'>Coronavirus Update</a></h2>"
    textOutput = "\n\n\nWashington Post Coronavirus Update:\nhttps://washingtonpost.com/coronavirus/"

    url = "https://washingtonpost.com/coronavirus/"
    driver = webdriver.Chrome()
    driver.get(url)

    update = driver.find_elements_by_tag_name("h1")[1]
    updateText = update.text
    updateLink = update.find_elements_by_tag_name("a")[0].get_attribute("href")

    htmlOutput += "<h4><a href='{1}'>{0}</a></h4>".format(updateText, updateLink)
    textOutput += "\n\nUpdate: {0}\nArticle: {1}".format(updateText, updateLink, updateLink)

    driver.quit()
    return htmlOutput, textOutput



def scrape_aljazeera():
    htmlOutput = "<br><h2>Al Jazeera News Updates</h2></br>"
    textOutput = "\n\n\nAl Jazeera News:\n"

    url = "https://aljazeera.com/Search/?q=covid-19"
    driver = webdriver.Chrome()
    driver.get(url)

    top3stories = driver.find_elements_by_class_name("topics-sec-item")[:3]

    htmlOutput += "<br><div style='display:flex;'>"
    for entry in top3stories:
        headline = entry.find_elements_by_class_name("topics-sec-item-head")[0]
        headlineLink = entry.find_elements_by_tag_name("a")[1].get_attribute("href")
        headlineText = headline.text
        description = entry.find_elements_by_class_name("topics-sec-item-p")[0].text
        imgLink = entry.find_elements_by_class_name("img-responsive")[0].get_attribute("src")

        htmlOutput += "<div style='width:250px;margin-right:25px;'><a href='{1}'><img style='max-width:250px;margin-right:30px;' src='{3}'></a><a href='{1}'><h3>{0}</h3></a><p>{2}</p></div>".format(headlineText, headlineLink, description, imgLink)
        textOutput += "\nHeadline: {0}\nDescription: {1}\nLink: {2}".format(headlineText, description, headlineLink)
    htmlOutput += "</div>"

    driver.quit()
    return htmlOutput, textOutput



def scrape_xinhua():
    htmlOutput = "<br><h2>Xinhua News Updates</h2></br>"
    textOutput = "\n\n\nXinhua News:\n"

    url = "http://search.news.cn/?keyWordAll=&keyWordOne=covid-19+wuhan+china&keyWordIg=&searchFields=0&sortField=0&url=&senSearch=1&lang=en#search/0/covid-19%20wuhan%20china/1/"
    driver = webdriver.Chrome()
    driver.get(url)

    time.sleep(.8)

    top3stories = driver.find_elements_by_class_name("news")[:3]

    htmlOutput += "<br><div style='display:flex;'>"
    for entry in top3stories:
        headline = entry.find_elements_by_tag_name("h2")[0]
        headlineLink = headline.find_elements_by_tag_name("a")[0].get_attribute("href")
        headlineText = headline.text
        description = entry.find_elements_by_class_name("newstext")[0].text
        try:
            imgLink = entry.find_elements_by_tag_name("img")[0].get_attribute("src")
        except:
            imgLink = ""
        htmlOutput += "<div style='width:250px;margin-right:25px;'><a href='{1}'><img style='max-width:250px;margin-right:30px;' src='{3}'></a><a href='{1}'><h3>{0}</h3></a><p>{2}</p></div>".format(headlineText, headlineLink, description, imgLink)
        textOutput += "\nHeadline: {0}\nDescription: {1}\nLink: {2}".format(headlineText, description, headlineLink)
    htmlOutput += "</div><br>"

    driver.quit()
    return htmlOutput, textOutput




## COMPILE MESSAGE FROM WEB-SCRAPING DATA

def compile_message():
    print("[{0}] gathering and compiling data".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    startTime = time.time()

    html = plaintext = ""
    html += "<html>"

    htmlAdd, plaintextAdd = scrape_google()
    html += htmlAdd
    plaintext += plaintextAdd

    htmlAdd, plaintextAdd = scrape_bbc()
    html += htmlAdd
    plaintext += plaintextAdd

    htmlAdd, plaintextAdd = scrape_washingtonpost()
    html += htmlAdd
    plaintext += plaintextAdd

    htmlAdd, plaintextAdd = scrape_aljazeera()
    html += htmlAdd
    plaintext += plaintextAdd

    htmlAdd, plaintextAdd = scrape_xinhua()
    html += htmlAdd
    plaintext += plaintextAdd
    
    
    html += "</html>\n"
    plaintext += "\n"

    endTime = time.time()
    print("-- Compiled and formatted all data. Time elapsed: {0:.2f} seconds.".format(endTime-startTime))
    return html, plaintext




## SEND UPDATE

def get_recipients():
    with open("subscribers.txt", "r") as f:
        recipients = f.readlines()
    return recipients


def send_update(update, plaintext):
    print("[{0}] sending email updates".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    startTime = time.time()

    ## Record message
    hname = "old-updates/{0}-Update.html".format(date.today())
    with open(hname, "w") as f:
        f.write(update)
        print("-- HTML Message:", hname)
    tname = "old-updates/{0}-Update.txt".format(date.today())
    with open(tname, "w") as f:
        f.write(update)
        print("-- Text Message:", tname)
    ##

    recipients = get_recipients()
    print("-- Recipients:", recipients)

    sender_email = "covid19globalupdate@gmail.com"
    email_password = "covid19updater"

    message = MIMEMultipart("alternative")
    message["Subject"] = "COVID-19 Update {0}".format(date.today())
    message["From"] = sender_email
    message.attach(MIMEText(plaintext, "text"))
    message.attach(MIMEText(update, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, email_password)
        #loop over recipients
        for receiver in recipients:
            message["To"] = receiver
            server.sendmail(sender_email, receiver, message.as_string())

    endTime = time.time()
    print("-- Sent all emails. Time elapsed: {0:.2f} seconds.".format(endTime-startTime))


    
def compile_and_send():
    print("[{0}] Starting Scheduled Run --".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    message, plaintext = compile_message()
    send_update(message, plaintext)
    print()




def main():
    print("Starting COVID-19 News Script\n")

    # Daily loop
    while True:
        if datetime.now().strftime("%H") == "12":
            compile_and_send()
        time.sleep(3600)
    

if __name__ == "__main__":
    main()
