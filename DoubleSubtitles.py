#!/usr/bin/env python
# coding: utf-8

import configparser
import io
import os
import time
import pysrt
import numpy as np
import pandas as pd
import subprocess
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import *
from TkinterDnD2 import *
from docx import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import chromedriver_autoinstaller


# открытие и исправление кодировки субтитров
def open_sub(s0):
    try:
        sub0 = pysrt.open(s0, encoding="utf-8")
    except:
        with io.open(s0, mode="r") as f:
            data = f.read()
        with io.open(s0, mode="w", encoding="utf-8-sig") as f:
            f.write(data)
        sub0 = pysrt.open(s0, encoding="utf-8")
    return sub0


# редактирование текста в субтитрах
def filter_sub(s0):
    remove_list = []
    # количество субтитров в файле
    for z in range(len(s0)):
        # удаление части текста, состоящего из всех больших букв без знаков пунктуации (прим. [текст] УЛИЦА СКРЕМПТОН)
        if s0[z].text.isupper() == False                 and re.findall('\n', s0[z].text) != []                 and s0[z].text[0:s0[z].text.find('\n')].isupper()                 and re.findall('[^\s\w]', s0[z].text[0:s0[z].text.find('\n')]) == []:
            s0[z].text = s0[z].text[s0[z].text.find('\n') + 1:]
        # красная строка
        s0[z].text = s0[z].text.replace("\n", " ")
        if sdh_var.get() == 1:
            # курсив, начало речи (прим. - Привет! - Здравствуй)
            s0[z].text = s0[z].text.replace("<i>", "").replace("</i>", "").replace("- ", "").replace("– ", "")
            # деление одного субтитра на слова
            word_list = []
            for word in s0[z].text.split():
                if len(word) > 1 and word[0] == "-":
                    word = word[1:]
                # заполнение списка
                word_list.append(word)
            # заполнение списка
            s0[z].text = ' '.join(word_list)
        if sdh_var.get() == 1                 and s0[z].text.find(":") != -1:
            # цикл полного избавления от речевого двоеточия (прим. ROSS:)
            while s0[z].text[0:s0[z].text.find(":") + 1].isupper()                     or s0[z].text[s0[z].text[0:s0[z].text.find(":")].rfind(" ") + 1:s0[z].text.find(":") + 1].isupper():
                if s0[z].text[0:s0[z].text.find(":") + 1].isupper():
                    s0[z].text = s0[z].text[s0[z].text.find(":") + 2:]
                else:
                    s0[z].text = s0[z].text[0:s0[z].text[0:s0[z].text.find(":")].rfind(" ")] + " " +                                  s0[z].text[s0[z].text.find(":") + 2:]
        # список символов
        symbol_list = ["(", ")", "[", "]"]
        # удаление всего текста, состоящего из всех больших букв без знаков пунктуации (прим. УЛИЦА СКРЕМПТОН)
        if s0[z].text.isupper()                 and re.findall('[^\s\w]', s0[z].text) == []                 and uppercase_var.get() == 1:
            remove_list.append(z)
            continue
        elif sdh_var.get() == 1:
            for x, y in list(zip(symbol_list, symbol_list[1:]))[::2]:
                # цикл полного избавления от скобок SDH (прим. [sighs])
                while s0[z].text.find(x) != -1                         and s0[z].text.find(y) != -1:
                    # [] = []
                    if s0[z].text == s0[z].text[s0[z].text.find(x):s0[z].text.find(y) + 1]:
                        remove_list.append(z)
                        break
                    # [] = [] ...
                    # второе условие and - непопадание []
                    elif s0[z].text[0:s0[z].text.find(y) + 1] == s0[z].text[s0[z].text.find(x):s0[z].text.find(y) + 1]                             and s0[z].text[s0[z].text.find(x):0] != s0[z].text[s0[z].text.find(x):s0[z].text.find(y) + 1]:
                        s0[z].text = s0[z].text[s0[z].text.find(y) + 2:]
                    # [] = ... []
                    elif s0[z].text[s0[z].text.find(x):] == s0[z].text[s0[z].text.find(x):s0[z].text.find(y) + 1]:
                        s0[z].text = s0[z].text[0:s0[z].text.find(x) - 1]
                    # [] = ... [] ...
                    else:
                        s0[z].text = s0[z].text[0:s0[z].text.find(x) - 1] + " " + s0[z].text[s0[z].text.find(y) + 2:]
    if remove_list != []:
        for i in reversed(remove_list):
            del s0[i]
    # переиндексация субтитров
    s0.clean_indexes()
    return s0


# создание датафрейма из субтитра
def dataframe_sub(sub,language):
    start_list, end_list, text_list = [],[],[]
    for i in range(0,len(sub)):
        start = sub[i].start.to_time()
        end = sub[i].end.to_time()        
        start_ms = start.hour*3600000 + start.minute*60000 + start.second*1000 + start.microsecond*0.001
        end_ms = end.hour*3600000 + end.minute*60000 + end.second*1000 + end.microsecond*0.001      
        start_list.append(start_ms) 
        end_list.append(end_ms)
        text_list.append(sub[i].text)
    data = {'start': start_list, 'end': end_list, 'language': language, 'text': text_list}
    return pd.DataFrame(data=data)


# объединение субтитров
def merge_sub(sub1, sub2, bar, driver):
    if space_var.get() == 1:
        space_sub = '\n&nbsp;\n'
    else:
        space_sub = '\n'
    sub1_df = dataframe_sub(sub1,"en")
    sub2_df = dataframe_sub(sub2,"ru")
    df = pd.concat([sub1_df, sub2_df], axis=0)
    df['sum'] = df[['start','end']].sum(axis=1)
    df['plus'] = (df['start'] + df['end'])/2
    df = df.sort_values(by = 'start', ascending = True)
    # агломеративная кластеризация
    if clusters_auto_var.get() == 1:
        clusters_list = []
        # оценка качества с помощью "силуэта"
        silhouette = [] 
        for i in np.linspace(0.2, 1, 20):
            root.update()
            threshold = float(i) * 10000
            clustering = AgglomerativeClustering(n_clusters=None,
                                                 distance_threshold=threshold).fit(df[['start','end']])
            clusters = clustering.labels_                                                                          
            clusters_list.append(len(pd.unique(clusters)))
            score = silhouette_score(df[['start','end']], clusters)
            silhouette.append(score)
        max_silhouette = np.argmax(silhouette)                      
        clustering = AgglomerativeClustering(n_clusters=clusters_list[max_silhouette]).fit(df[['start','end']])
    else: 
        threshold = float(clusters_manual_entry.get()) * 10000
        clustering = AgglomerativeClustering(n_clusters=None,
                                             distance_threshold=threshold,
                                             linkage=clusters_method_combobox.get()).fit(df[['start','end']])
    clusters = clustering.labels_
    # добавление найденных кластеров
    df['cluster'] = clusters
    bar_subs = float(bar) / float(len(pd.unique(clusters)))
    # создание нового файла субтитров
    double_sub = pysrt.SubRipFile(encoding='utf-8')
    translate_list = pysrt.SubRipFile(encoding='utf-8')
    for n, i in enumerate(pd.unique(clusters)):
        root.update()
        progressBar['value'] += bar_subs
        df_en = df[(df['language'] == 'en') & (df['cluster'] == i)]
        df_ru = df[(df['language'] == 'ru') & (df['cluster'] == i)]
        df_group_en = df_en.groupby('cluster').agg({'text':' '.join, 'start': min, 'end': max, 'language':'first'})
        df_group_ru = df_ru.groupby('cluster').agg({'text':' '.join, 'start': min, 'end': max, 'language':'first'})
        df_group = df_group_en.merge(df_group_ru,
                                     on=['cluster','text','start','end','language'],
                                     how='outer').groupby('cluster').agg({'text':space_sub.join,
                                                                          'start':'first',
                                                                          'end':'first',
                                                                          'language':''.join})
        sub = pysrt.SubRipItem(index=n+1,
                               start=int(df_group.iloc[0]['start']),
                               end=int(df_group.iloc[0]['end']),
                               text=str(df_group.iloc[0]['text']))
        double_sub.append(sub)
        if translate_var.get() == 1 and df_group['language'].values == 'en':
            translate_list.append(sub)
    if translate_var.get() == 1 and translate_list:
        translate_sub(translate_list, bar, driver)
    # переиндексация субтитров
    double_sub.clean_indexes()
    return double_sub


# основной цикл
def begin_sub(s1, s2):
    progressBar['value'] = 0
    if (s1 and s2 and len(s1) == len(s2) and output_path_entry.get()) or         (s1 and output_path_entry.get() and translate_settings_var.get() == 2 and translate_var.get() == 1):
        progressbar_wait(10)
        if translate_var.get() == 1:
            # открытие браузера для перевода субтитров
            driver = translate_webdriver("start")
            if translate_settings_var.get() == 2:
                s2 = [' ' for i in range(0, len(s1))]
        else:
            driver = None   
        # создание папки при ее отсутствии
        if not os.path.exists(output_path_entry.get()):
            os.makedirs(output_path_entry.get())
        for s1s2 in list(zip(s1, s2)):
            for x, s0 in enumerate(s1s2):
                # присвоение субтитров, открытие и исправление неверной кодировки, редактирование текста в субтитрах   
                if x == 0:
                    sub1 = filter_sub(open_sub(s0))
                elif (x == 1 and translate_settings_var.get() != 2 and translate_var.get() == 1) or                     (x == 1 and translate_var.get() == 0):
                    sub2 = filter_sub(open_sub(s0))
            bar = 80 / len(s1)
            # объединение или полный перевод субтитров
            if translate_settings_var.get() == 2 and translate_var.get() == 1:
                double_sub = translate_sub(sub1, bar, driver)
                file_type = "translate"
            else:
                double_sub = merge_sub(sub1, sub2, bar, driver)
                file_type = "double"
            # сохранение файла
            file_name = os.path.basename(s1s2[0])
            if os.path.basename(s1s2[0]).find("_Track") != -1:
                file_path = output_path_entry.get() + file_name[:-12] + '.' + file_type + '.srt'
            else:
                file_path = output_path_entry.get() + file_name[:-4] + '.' + file_type + '.srt'
            double_sub.save(file_path, encoding='utf-8')
            sub1_listbox.delete(0)
            sub2_listbox.delete(0)
        del s1[:]
        del s2[:]
        # закрытие браузера
        if translate_var.get() == 1:
            driver = translate_webdriver("end", driver)
        progressbar_wait(10)
        # открытие папки
        # os.startfile(output_path_entry.get())        
        subprocess.Popen(r'explorer /select, "'+ os.path.normpath(file_path) + '"')
    else:
        if not s1 and not s2:
            messagebox.showerror("Error", "     Add subtitles to input lists!")
        elif not s1 and s2:
            messagebox.showerror("Error", "     Add Upper subtitles!")
        elif not output_path_entry.get():
            messagebox.showerror("Error", "     Choose output folder!")            
        elif not s2 and s1:
            messagebox.showerror("Error", "     Add Lower subtitles!")
        elif s1 and s2 and len(s1) != len(s2):
            messagebox.showerror("Error",
                                   "     There must be the same number of Upper and Lower                 subtitles!")

        else:
            messagebox.showerror("Error", "     Something Wrong!")
    progressBar['value'] = 0


def translate_webdriver(action, driver=None):  
    if action == 'start':
        # настройки для гугл хром
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920x1080")
        root.update()
        chromedriver_autoinstaller.install(cwd=True)
        driver = webdriver.Chrome(options=options)
        root.update()
        url = 'https://translate.yandex.ru/doc'
        root.update()
        driver.get(url)
        root.update()
    elif action == 'end':
        driver.quit()
    return driver
        
    
# перевод субтитров с помощью Yandex
def translate_sub(subs, bar, driver):
    try:
        # создание файла для загрузки на сайта
        document = Document()
        for sub in subs:
            document.add_paragraph(sub.text)
        document.save('translate.docx')
        # загрузка файла на сайт и нахождение элемента
        driver.find_element_by_xpath("//input[@id='docInput']").send_keys(os.path.abspath('translate.docx'))
        root.update()
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//span[@id='progress']"), '100%'))
        root.update()
        # удаление файла для перевода
        os.remove("translate.docx")
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH, "//iframe[@id='targetFrame' and @name='targetFrame']")))
        elements = driver.find_elements_by_xpath("//p[@style='margin-bottom: 0.14in']")
        # объединение оригинального текста с переведенным текстом
        for i, element in enumerate(elements):
            root.update()
            if translate_settings_var.get() == 2 and translate_var.get() == 1:
                progressBar['value'] += bar/float(len(elements))
            subs[i].text += "\n" + "&nbsp;" + "\n" + element.text.replace("- ", "")
        # обновление/возврат страницы
        driver.switch_to.default_content()
    except:
        messagebox.showerror("Error", "     Try again later!")
    return subs


# плавный прогрессбар
def progressbar_wait(bar):
    for i in range(0, int(bar * 10)):
        root.update()
        speed = float(1) / 10
        progressBar['value'] += speed
        time.sleep(float(speed) / bar)


# добавление файла
def add_sub(s1, s2, num):
    subs = sorted(filedialog.askopenfilenames(
        title='Choose subtitles',
        initialdir=os.path.expanduser("~/Desktop"),
        filetypes=[
            ("SRT", "*.srt"),
            ("All files", "*")]))
    if subs:
        if num == 1:
            for sub in subs:
                sub1_listbox.insert(END, os.path.basename(sub))
                s1.append(sub)
        elif num == 2:
            for sub in subs:
                sub2_listbox.insert(END, os.path.basename(sub))
                s2.append(sub)


# открытие файла в листбоксе интерфейса
def start_sub(num):
    if sub1_listbox.curselection() != () or sub2_listbox.curselection() != ():
        if num == 1:
            os.startfile(s1[sub1_listbox.curselection()[0]])
        if num == 2:
            os.startfile(s2[sub2_listbox.curselection()[0]])


# удаление файла в листбоксе интерфейса
def remove_sub(num):
    if num == 1:
        if sub1_listbox.curselection() != ():
            del s1[sub1_listbox.curselection()[0]]
            sub1_listbox.delete(sub1_listbox.curselection()[0])
    elif num == 2:
        if sub2_listbox.curselection() != ():
            del s2[sub2_listbox.curselection()[0]]
            sub2_listbox.delete(sub2_listbox.curselection())


# очистка всех файлов
def clear_sub(num):
    if num == 1:
        del s1[:]
        sub1_listbox.delete(0, END)
    elif num == 2:
        del s2[:]
        sub2_listbox.delete(0, END)


# создание файла настроек
def create_config(config, path):
    config.add_section("settings")
    config.set("settings", "output_path_entry", "")
    config.set("settings", "space_checkbutton", "1")
    config.set("settings", "uppercase_checkbutton", "0")
    config.set("settings", "sdh_checkbutton", "1")
    config.set("settings", "clusters_auto_checkbutton", "1")     
    config.set("settings", "clusters_manual_entry_button", "0.5")   
    config.set("settings", "clusters_method_combobox", "ward")
    config.set("settings", "translate_checkbutton", "0")
    config.set("settings", "translate_settings_radiobutton", "1")
    with open(path, "w") as config_file:
        config.write(config_file)


# конфиг
def get_config(path):
    config = configparser.ConfigParser()
    if not os.path.exists(path):
        create_config(config, path)
    config.read(path)
    return config


# сохранение конфига
def set_config(num):
    if num == 1:
        config.set("settings", "uppercase_checkbutton", str(uppercase_var.get()))
    elif num == 2:
        config.set("settings", "translate_checkbutton", str(translate_var.get()))
    elif num == 3:
        config.set("settings", "sdh_checkbutton", str(sdh_var.get()))
    elif num == 4:
        config.set("settings", "space_checkbutton", str(space_var.get()))
    elif num == 5:
        config.set("settings", "output_path_entry", str(output_path_entry.get()))
    elif num == 6:
        config.set("settings", "translate_settings_radiobutton", str(translate_settings_var.get()))
    elif num == 7:
        config.set("settings", "clusters_manual_entry_button", str(clusters_manual_entry.get())) 
    elif num == 8:
        config.set("settings", "clusters_auto_checkbutton", str(clusters_auto_var.get()))
    elif num == 9:
        config.set("settings", "clusters_method_combobox", str(clusters_method_combobox.get()))
    with open(config_path, "w") as config_file:
        config.write(config_file)


# назначение папки вывода
def set_output():
    folder0 = filedialog.askdirectory()
    output_path_entry.configure(state="normal")
    if folder0:
        output_path_entry.delete(0, END)
        output_path_entry.insert(0, folder0 + "/")
    output_path_entry.configure(state="disabled")
    set_config(5)
    

def set_clusters():
    if clusters_auto_var.get() == 0:
        clusters_manual_entry.configure(state="normal")
        clusters_method_combobox.configure(state="readonly")
        label1.configure(state="normal")
        label2.configure(state="normal")
        label3.configure(state="normal")
        label4.configure(state="normal")        
    else:
        clusters_manual_entry.configure(state="disabled")
        clusters_method_combobox.configure(state="disabled")
        label1.configure(state="disabled")
        label2.configure(state="disabled")
        label3.configure(state="disabled")
        label4.configure(state="disabled")
    set_config(8)
    
    
def set_translate(num):
    if num == 1:
        if translate_var.get() == 1:
            if translate_settings_var.get() == 2:
                translate_button.configure(state="normal")
                merge_button.configure(state="disabled")
            combobox1.configure(state="readonly")
            combobox2.configure(state="readonly")      
            translate_settings_radiobutton_1.configure(state="readonly")
            translate_settings_radiobutton_2.configure(state="readonly")
            label5.configure(state="normal")
            label6.configure(state="normal")         
        else:
            if translate_settings_var.get() == 2:
                merge_button.configure(state="normal")
            translate_button.configure(state="disabled")
            combobox1.configure(state="disabled")
            combobox2.configure(state="disabled")
            translate_settings_radiobutton_1.configure(state="disabled")
            translate_settings_radiobutton_2.configure(state="disabled")
            label5.configure(state="disabled")
            label6.configure(state="disabled")       
        set_config(2)     
    elif num == 2:
        if translate_settings_var.get() == 2:
            translate_button.configure(state="normal")
            merge_button.configure(state="disabled")
        else:
            translate_button.configure(state="disabled")
            merge_button.configure(state="normal")
        set_config(6)

        
# перетаскивание файлов
def drop(event):
    if event.data:
        files = sorted(re.findall(r'\{.*?\}|\S+', event.data))
        for f in files:
            if f[0] == "{" and f[-1] == "}":
                f = f[1:-1]
            if f.lower().endswith('.srt'):
                if os.path.exists(f):
                    event.widget.insert('end', os.path.basename(f))
                    if event.widget == sub1_listbox:
                        s1.append(f)
                    elif event.widget == sub2_listbox:
                        s2.append(f)
                else:
                    messagebox.showerror("Error", "     Something Wrong!")
            else:
                messagebox.showerror("Error", "     Only SRT file type!")
    return event.action


# восстановление ссылки иконки приложения
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


s1 = []  # список для файлов английских субтитров
s2 = []  # список для файлов русских субтитров
# файл настроек
config_path = "config.ini"
config = get_config(config_path)
root = TkinterDnD.Tk()  # создание интерфейса
# иконка приложения и google chrome
try:
    image_path = resource_path("DoubleSubtitles.ico")
except:
    image_path = "DoubleSubtitles.ico"
root.iconbitmap(image_path)
root.wm_title('Double Subtitles')  # название окна

Label(text="     ").grid(row=0, column=0)
Label(text="     ").grid(row=4, column=0)
Label(text="     ").grid(row=6, column=0)
Label(text="     ").grid(row=0, column=6)
Label(text="     ").grid(row=9, column=0)
Label(text="     ").grid(row=11, column=0)
Label(text="     ").grid(row=13, column=0)
Label(text="     ").grid(row=15, column=12)

Label(text="Upper subtitles:").grid(row=1, column=1, columnspan=2, sticky=W)
Label(text="Lower subtitles:").grid(row=1, column=7, columnspan=2, sticky=W)

sub1_listbox = Listbox()
sub1_scrollbar = Scrollbar(orient="vertical")
sub1_listbox.config(yscrollcommand=sub1_scrollbar.set)
sub1_scrollbar.configure(command=sub1_listbox.yview)
sub1_listbox.grid(row=2, column=1, columnspan=4, sticky=N + S + W + E)
sub1_scrollbar.grid(row=2, column=5, sticky=N + S)
sub1_listbox.drop_target_register(DND_FILES)
sub1_listbox.dnd_bind('<<Drop>>', drop)
sub1_listbox.bind('<Double-Button-1>', lambda event: start_sub(1))
sub1_listbox.bind('<Return>', lambda event: start_sub(1))
sub1_listbox.bind('<Delete>', lambda event: remove_sub(1))

sub2_listbox = Listbox()
sub2_scrollbar = Scrollbar(orient="vertical")
sub2_listbox.config(yscrollcommand=sub2_scrollbar.set)
sub2_scrollbar.configure(command=sub2_listbox.yview)
sub2_listbox.grid(row=2, column=7, columnspan=4, sticky=N + S + W + E)
sub2_scrollbar.grid(row=2, column=11, sticky=N + S)
sub2_listbox.drop_target_register(DND_FILES)
sub2_listbox.dnd_bind('<<Drop>>', drop)
sub2_listbox.bind('<Double-Button-1>', lambda event: start_sub(2))
sub2_listbox.bind('<Return>', lambda event: start_sub(2))
sub2_listbox.bind('<Delete>', lambda event: remove_sub(2))

Button(text="Add", width=20, command=lambda: add_sub(s1, s2, 1)).grid(row=3, column=1, columnspan=2, sticky=W + E)
Button(text="Remove", width=10, command=lambda: remove_sub(1)).grid(row=3, column=3, columnspan=1, sticky=W + E)
Button(text="Clear all", width=10, command=lambda: clear_sub(1)).grid(row=3, column=4, columnspan=1, sticky=W + E)
Button(text="Add", width=20, command=lambda: add_sub(s1, s2, 2)).grid(row=3, column=7, columnspan=2, sticky=W + E)
Button(text="Remove", width=10, command=lambda: remove_sub(2)).grid(row=3, column=9, columnspan=1, sticky=W + E)
Button(text="Clear all", width=10, command=lambda: clear_sub(2)).grid(row=3, column=10, columnspan=1, sticky=W + E)

output_path_entry = Entry()
output_path_entry.insert(0, config.get("settings", "output_path_entry"))
output_path_entry.configure(state="disabled")
output_path_entry.grid(row=5, column=3, columnspan=9, sticky=N + S + W + E)
Button(text="Output folder", width=20, command=lambda: set_output()).grid(row=5, column=1, columnspan=2, sticky=W + E)

uppercase_var = IntVar()
uppercase_var.set(config.get("settings", "uppercase_checkbutton"))
uppercase_checkbutton = Checkbutton(text='Delete uppercase subs',
                                    variable=uppercase_var,
                                    command=lambda: set_config(1)).grid(row=7, column=3, columnspan=3, sticky=W)
sdh_var = IntVar()
sdh_var.set(config.get("settings", "sdh_checkbutton"))
sdh_checkbutton = Checkbutton(text='Remove SDH subs',
                              variable=sdh_var,
                              command=lambda: set_config(3)).grid(row=8, column=1, columnspan=2, sticky=W)
space_var = IntVar()
space_var.set(config.get("settings", "space_checkbutton"))
space_checkbutton = Checkbutton(text='Space between subs',
                                variable=space_var,
                                command=lambda: set_config(4)).grid(row=7, column=1, columnspan=2, sticky=W)
clusters_auto_var = IntVar()
clusters_auto_var.set(config.get("settings", "clusters_auto_checkbutton"))
clusters_auto_checkbutton = Checkbutton(text='Automatic clustering',
                                        variable=clusters_auto_var,
                                        command=lambda: set_clusters()).grid(row=8, column=3, columnspan=2, sticky=W)
label1 = Label(text="Clustering coefficient:")
label1.grid(row=9, column=1, columnspan=2, sticky=W)
label2 = Label(text="default: 0.5")
label2.grid(row=9, column=4, columnspan=2, padx=5, sticky=W)

clusters_manual_entry = Entry(justify='center', width=12)
clusters_manual_entry.grid(row=9, column=3, sticky=W + E)
clusters_manual_entry.insert(0, config.get("settings", "clusters_manual_entry_button"))
clusters_manual_entry.bind('<FocusOut>', lambda event: set_config(7))

label3 = Label(text="Clustering method:")
label3.grid(row=10, column=1, columnspan=2, sticky=W)
label4 = Label(text="default: ward")
label4.grid(row=10, column=4, columnspan=2, padx=5, sticky=W)

clusters_method_combobox = Combobox(state="readonly", values=['single','average','complete','ward'], width=5, justify='center')
clusters_method_combobox.set(config.get("settings", "clusters_method_combobox"))
clusters_method_combobox.grid(row=10, column=3, sticky=W + E)
clusters_method_combobox.bind('<<ComboboxSelected>>', lambda event: set_config(9))
   
merge_button = Button(text="Merge", width=20, command=lambda: begin_sub(s1, s2))
merge_button.grid(row=12, column=3, columnspan=2, sticky=W + E)
set_clusters() 

label5 = Label(text="From:", justify='center')
label5.grid(row=7, column=9, columnspan=1)
label6 = Label(text="To:", justify='center')
label6.grid(row=8, column=9, columnspan=1)

combobox1 = Combobox(values="en", width=5, state='readonly', justify='center')
combobox1.set('en')
combobox1.grid(row=7, column=10, sticky=W + E)
combobox2 = Combobox(values="ru", width=5, state='readonly', justify='center')
combobox2.set('ru')
combobox2.grid(row=8, column=10, sticky=W + E)

translate_var = IntVar()
translate_var.set(config.get("settings", "translate_checkbutton"))
translate_checkbutton = Checkbutton(text='Translate subs',
                               variable=translate_var,
                               command=lambda: set_translate(1)).grid(row=7, column=7, columnspan=2, sticky=W)
translate_settings_var = IntVar()
translate_settings_var.set(config.get("settings", "translate_settings_radiobutton"))
translate_settings_radiobutton_1 = Radiobutton(text='translate unpaired subs',
                                          variable=translate_settings_var,
                                          value=1,
                                          command=lambda: set_translate(2))
translate_settings_radiobutton_2 = Radiobutton(text='translate all subs',
                                          variable=translate_settings_var,
                                          value=2,
                                          command=lambda: set_translate(2))
translate_settings_radiobutton_1.grid(row=9, column=7, columnspan=2)
translate_settings_radiobutton_2.grid(row=9, column=9, columnspan=2)

translate_button = Button(text="Translate", width=20, command=lambda: begin_sub(s1, s2))
translate_button.grid(row=12, column=7, columnspan=2, sticky=W + E)
set_translate(1)
set_translate(2)

progressBar = Progressbar(orient='horizontal', mode='determinate', maximum=100, value=0)
progressBar.grid(row=14, column=1, columnspan=11, sticky=W + E)
# половина ширины/высоты экрана, ширины/высоты окна
positionRight = int(root.winfo_screenwidth() / 2 - 720 / 2)
positionDown = int(root.winfo_screenheight() / 2 - 480 / 2)
# окно в центре 'экрана'.
root.geometry("+{}+{}".format(positionRight, positionDown))
root.mainloop()
