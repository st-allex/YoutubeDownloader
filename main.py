from pytube import YouTube
from tkinter import (Tk, ttk,
                    Entry as tkEntry,
                    Label as tkLabel,
                    Text as tkText,
                    Button as tkButton,
                    Frame as tkFrame,
                    StringVar as tkStringVar,
                    PhotoImage as tkPhotoImage)
from requests import get as get_url
from io import BytesIO
from PIL import Image as iImage, ImageTk as iImageTk

yt = None
dict_mywnd = None
bCheck = False
# 0 - console, 1 - tkinter
gui_mode = 1


def int2str(cur_int: int) -> str:
    """ Get string from integer with format """
    n = str(cur_int)[::-1]
    return '\u00A0'.join(n[i:i+3] for i in range(0, len(n), 3))[::-1]


def on_progress(stream, total_size, byte_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - byte_remaining
    percent = (bytes_downloaded / total_size) * 100
    prog_inf = f"{int(percent)}% [{int2str(bytes_downloaded)} / {int2str(total_size)}]"
    if gui_mode==0:
        print("\r" + chr(9646)*int(percent) + chr(9647)*(100-int(percent)) + ' | ' + prog_inf, end="")
    elif gui_mode==1:
        dict_mywnd['pbDownload'].config(value=percent)
        dict_mywnd['td_style'].configure('text.Horizontal.TProgressbar', text=prog_inf)
        dict_mywnd['pbDownload'].update()
    else:
        pass


def initWnd():
    rez_dict = dict()
    newwnd = Tk()


    rez_dict['mywnd'] = newwnd

    for col_ind in range(2):
        newwnd.columnconfigure(index=col_ind, weight=1)
    for row_ind in range(6):
        newwnd.rowconfigure(index=row_ind, weight=1)

    newwnd.config(bg='#336699') #, width=600, height=600)
    newwnd.title("Youtube downloader")
    #newwnd.iconbitmap("ytDownload.ico")
    newwnd.resizable(width=False, height=False)

    yt_url = tkEntry(newwnd, foreground='#003366')
    rez_dict['yt_url'] = yt_url
    yt_url.insert(0, 'https://www.youtube.com/watch?v=ibf2u-rVb6o')
    yt_url.grid(row=0, column=0, columnspan=2, sticky='swen', padx=5, pady=5)

    thumbnail_default = tkPhotoImage(file='thumbnail.png')
    prev_img = tkLabel(newwnd)
    rez_dict['prev_img'] = prev_img
    prev_img.config(image=thumbnail_default, width=320, height=190)
    prev_img.image = thumbnail_default
    prev_img.grid(row=1, column=0, rowspan=2, sticky='swen', padx=5, pady=5)

    btnCheck = tkButton(newwnd,
                        text='Проверить скачиваемое видео.',
                        height=1,
                        bg='#003366',
                        activebackground='#6699CC',
                        font=('Arial', 10, 'bold'),
                        foreground='#ffff00',
                        activeforeground='#0000ff',
                        command=check_cmd)
    rez_dict['btnCheck'] = btnCheck
    btnCheck.grid(row=1, column=1, sticky='swen', padx=5, pady=5)

    info_img = tkText(newwnd,
                        height=5,
                        bg='#99ccff',
                        font=('Arial', 11, 'normal'),
                        wrap='word',
                        state='disabled',
                        spacing3=7)
    rez_dict['info_img'] = info_img
    info_img.grid(row=2, column=1, sticky='swen', padx=5, pady=5)

    fr_param = tkFrame(newwnd, bg='#4477aa', height=300)
    rez_dict['fr_param'] = fr_param
    fr_param.grid(row=3, column=0, columnspan=2, sticky='swen', padx=5, pady=5)

    dict_qualities = {'Низкое':0, 'Высокое':1}
    list_qualities = list(dict_qualities.keys())
    cur_quality = tkStringVar()
    fr_cb_quality = ttk.Combobox(fr_param,
                                    foreground='blue',
                                    width=8,
                                    background='yellow',
                                    state='readonly',
                                    values=list_qualities,
                                    textvariable=cur_quality)
    rez_dict['fr_cb_quality'] = fr_cb_quality
    fr_cb_quality.grid(row=0, column=0, sticky='swen', padx=5, pady=5)
    cur_quality.set('kjh')
    #cur_quality.trace('w', handler_set_quality)

    td_style = ttk.Style()
    rez_dict['td_style'] = td_style
    td_style.theme_use('classic')
    td_style.layout('text.Horizontal.TProgressbar',
                   [('Horizontal.Progressbar.trough',
                     {'children': [('Horizontal.Progressbar.pbar',
                                    {'side': 'left', 'sticky': 'ns'})],
                      'sticky': 'nswe'}),
                    ('Horizontal.Progressbar.label', {'sticky': ''})])
    td_style.configure('text.Horizontal.TProgressbar', text='')

    pbDownload = ttk.Progressbar(newwnd, style='text.Horizontal.TProgressbar')
    rez_dict['pbDownload'] = pbDownload
    pbDownload.grid(row=4, column=0, columnspan=2, sticky='swen', padx=5, pady=5)

    btnDownload = tkButton(newwnd,
                            text='Скачать видео',
                            height=1,
                            bg='#003366',
                            activebackground='#6699CC',
                            font=('Arial', 10, 'bold'),
                            foreground='#ffff00',
                            activeforeground='#0000ff',
                            command=download_cmd)
    rez_dict['btnDownload'] = btnDownload
    btnDownload.grid(row=5, column=0, columnspan=2, sticky='swen', padx=5, pady=5)

    return rez_dict

def handler_set_quality(*args):
    print('handler_set_quality')

def clear_prev_info():
    thumbnail_default = tkPhotoImage(file='thumbnail.png')
    dict_mywnd['prev_img'].image = thumbnail_default
    dict_mywnd['prev_img'].config(image=thumbnail_default, width=320, height=190)
    dict_mywnd['info_img'].config(state='normal')
    dict_mywnd['info_img'].delete("1.0", "end")
    dict_mywnd['info_img'].config(state='disabled')


def msg_no_img_inf():
    dict_mywnd['info_img'].config(state='normal')
    dict_mywnd['info_img'].delete("1.0", "end")
    dict_mywnd['info_img'].insert("end", 'Сначала проверьте скачиваемое видео.' + '\n')
    dict_mywnd['info_img'].config(state='disabled')


def set_thumbnail(thumbnail_url, thumbnail_lbl):
    global bCheck
    response = get_url(thumbnail_url)
    if response.status_code!=200:
        dict_mywnd['info_img'].config(state='normal')
        dict_mywnd['info_img'].insert("end", "Thumbnail not found\n")
        dict_mywnd['info_img'].config(state='disabled')
    else:
        img_from_url = iImageTk.PhotoImage(iImage.open(BytesIO(response.content)).resize((320, 190), iImage.LANCZOS))
        thumbnail_lbl.config(image=img_from_url, width=320, height=190)
        thumbnail_lbl.image = img_from_url
        bCheck = True


def set_info_img(oYT, info_img_txt):
    h = oYT.length // 3600
    s = oYT.length - h*3600
    m = s // 60
    s = s - m*60
    info_img_txt.config(state='normal')
    info_img_txt.insert("end", 'ЗАГОЛОВОК: ' + oYT.title + '\n')
    info_img_txt.insert("end", 'АВТОР: ' + oYT.author + '\n')
    info_img_txt.insert("end", 'ДАТА ПУБЛИКАЦИИ: ' + str(oYT.publish_date) + '\n')
    info_img_txt.insert("end", 'ПРОДОЛЖИТЕЛЬНОСТЬ ВИДЕО: ' + str(h) + ' ч ' + str(m) + ' м ' + str(s) + ' с')
    info_img_txt.config(state='disabled')


def get_yt(yt_url):
    return YouTube(yt_url, on_progress_callback=on_progress)


def download_cmd():
    if bCheck:
        file_name = ''
        download_file(yt, file_name)
    else:
        msg_no_img_inf()


def download_file(oYT, file_name):
    oYT.streams.get_highest_resolution().download(file_name)


def check_cmd():
    global yt
    clear_prev_info()
    yt = get_yt(dict_mywnd['yt_url'].get())
    set_thumbnail(yt.thumbnail_url, dict_mywnd['prev_img'])
    set_info_img(yt, dict_mywnd['info_img'])


def main_cons():
    download_file(get_yt(input('Введите ссылку youtube: ')), input('Укажите путь файла: '))
    #print("\n" + Path2SavedVideo)


def main_gui():
    global dict_mywnd
    dict_mywnd = initWnd()
    dict_mywnd['mywnd'].mainloop()


def main():
    #main_cons()
    main_gui()



if __name__ == "__main__":
    main()

