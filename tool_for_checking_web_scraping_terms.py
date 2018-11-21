import os

from bs4 import BeautifulSoup
import urllib, urllib.request, requests
import tkinter
from tkinter import *

#folder_path = os.getcwd()
folder_path = r'C:\Users\aasa9247\Desktop\Research-Current\Buildsystem\Automatic Tools\GitHub-AutomationTools\tool_for_checking_if_website_allows_text_scraping'
# data-tags are the tags used for explaining the conditions of using the
# content in the weblink
file_name = '\\data_tags.txt'
file_path = folder_path + file_name

with open(file_path, encoding="utf-8") as data_file:
        content = data_file.readlines()
        data_tags = [l.strip() for l in content]

def check_for_data_tags(url):
    '''return true if found a match for the data tags or false if found
    no match for the data tags'''
    with open(file_path, encoding="utf-8") as data_file:
        content = data_file.readlines()
        data_tags = [l.strip() for l in content]

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    imp_links = []

    for link in soup.find_all('a', href=True):

        ref_link = link.get('href')
        num_tag = len(set(ref_link.split('/')).intersection(set(data_tags)))
        if num_tag > 0:
            imp_links.append(ref_link)
        else:
            continue
    return imp_links

def urls2text(links):
    '''extract text from multiple links to one string'''
    all_text = ''
    for link in links:
        #print(link)
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        paras = soup.find_all('p')
        for para in paras:
            #print(para)
            all_text = all_text + ' ' + para.getText()
    return all_text

def clean_text(text):

    import re
    from nltk.corpus import stopwords

    text = text.lower()
    punc = '!"#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~'
    exclud = set(punc) #list of punctuation
    text = re.sub(r'[0-9]+', r' ', text)
    text = re.sub(' +', ' ', text)
    text = re.sub('\. +', '. ', text)
    text = ''.join(ch for ch in text if ch not in exclud)
    text = re.sub('( \. )+', ' ', text)
    text = re.sub('\.+ ', '. ', text)
    text = re.sub(' \. ', ' ', text)
    return text

def text2binary_for_scrape(text):
    '''extract sentence that contains important information about data usage'''
    full_text = clean_text(text)
    full_text_sent = full_text.split('. ')
    full_tok_sent = []
    for sent in full_text_sent:
        full_tok_sent.append(sent.split(' '))

    file_path = folder_path + '\\data_usage_terms_tags.txt'

    with open(file_path, encoding="utf-8") as data_file:
        content = data_file.readlines()
        data_usage_tags = [l.strip() for l in content]

    max_num_common_terms = 0
    imp_tok_sent = ''
    num_no_term = ''

    for tok_sent in full_tok_sent:
        msg = 'Web scraping terms are unclear to our system. Please check\
        the terms manually'
        num_common_terms = len(set(tok_sent).intersection(set(data_usage_tags)))
        num_no_term = len(set(tok_sent).intersection(set(['no', 'not'])))

        #print(num_common_terms, num_no_term)
        if num_common_terms > max_num_common_terms:
            max_num_common_terms = num_common_terms
            imp_tok_sent = tok_sent
        else:
            continue

        if num_no_term >= 1:
            can_scrape = 'no'
            sent = ' '.join(imp_tok_sent)
            msg = 'You cannot scrape text from the website. Here are more\
             details from the url: ' + ' "' + sent + '"'

        else:
            can_scrape = 'not sure'
            msg = 'Please check the terms as they are complicated to\
             understand by our system'
            continue
    return msg

def start_gui():
    window = tkinter.Tk()
    window.title('Check Web Scraping Terms Tool')
    window.geometry('400x100')

    label_tag = Label(window, text = 'URL')
    label_tag.pack(side = LEFT)
    input_button = Entry(window, width = 70, bd = 5)
    input_button.pack(expand = True, side = RIGHT)

    def tk_store():
        global url
        url = input_button.get()
        from tkinter import messagebox
        msgbox = messagebox.showinfo( 'Check Web Scraping Terms Tool',\
         'Please wait, while we analyze the url entered')

    def tk_close_window ():
        window.destroy()

    check_button = Button(window, text = 'Check',\
     command = lambda:[tk_store(), tk_close_window()])
    check_button.place(x = 175,y = 70)

    window.mainloop()

def close_gui(final_msg):
    window = tkinter.Tk()
    window.title('Check Web Scraping Terms Tool')

    var = StringVar()
    msg_label = Message(window, textvariable = var, relief = RAISED )
    var.set(final_msg)
    msg_label.pack()

    window.mainloop()
    window.after(30000, lambda: window.destroy())

start_gui()
links = check_for_data_tags(url)
text = urls2text(links)
final_msg = text2binary_for_scrape(text)

close_gui(final_msg)
