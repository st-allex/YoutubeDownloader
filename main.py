from pytube import YouTube
from tkinter import (Tk, Entry as tkEntry,
                     Label as tkLabel,
                     Text as tkText,
                     Button as tkButton,
                     PhotoImage as tkPhotoImage)
from requests import get as get_url
from io import BytesIO
from PIL import Image as iImage, ImageTk as iImageTk

yt = None
dict_mywnd = None
bCheck = False


def int2str(cur_int: int) -> str:
    """ Get string from integer with format """
    n = str(cur_int)[::-1]
    return '\u00A0'.join(n[i:i+3] for i in range(0, len(n), 3))[::-1]


def on_progress(stream, total_size, byte_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - byte_remaining
    percent = (bytes_downloaded / total_size) * 100
    print("\r" + chr(9646)*int(percent) + chr(9647)*(100-int(percent)) + f" {int(percent)}% " +
                                        f"[{int2str(bytes_downloaded)} / {int2str(total_size)}]", end="")


def initWnd():
    rez_dict = dict()
    newwnd = Tk()
    rez_dict['mywnd'] = newwnd
    newwnd.config(bg='#336699', width=600, height=600)
    newwnd.title("Youtube downloader")
    newwnd.resizable(width=False, height=False)

    yt_url = tkEntry(newwnd,
                     width=72,
                     foreground='#003366')
    rez_dict['yt_url'] = yt_url
    yt_url.insert(0, 'https://www.youtube.com/watch?v=ibf2u-rVb6o')
    yt_url.place(x=10, y=10)

    thumbnail_default = tkPhotoImage(file='thumbnail.png')
    prev_img = tkLabel(newwnd)
    rez_dict['prev_img'] = prev_img
    prev_img.config(image=thumbnail_default, width=320, height=190)
    prev_img.image = thumbnail_default
    prev_img.place(x=10, y=40)

    btnCheck = tkButton(newwnd,
                    text='Проверить скачиваемое видео.',
                    width=32,
                    height=1,
                    bg='#003366',
                    activebackground='#6699CC',
                    font=('Arial', 10, 'bold'),
                    foreground='#ffff00',
                    activeforeground='#0000ff',
                    command=check_cmd)
    rez_dict['btnCheck'] = btnCheck
    btnCheck.place(x=340, y=40)

    info_img = tkText(newwnd,
                    width=31,
                    height=6,
                    bg='#99ccff',
                    font=('Arial', 11, 'normal'),
                    wrap='word',
                    state='disabled',
                    spacing3=7)
    rez_dict['info_img'] = info_img
    info_img.place(x=340, y=75)

    btnDownload = tkButton(newwnd,
                    text='Скачать видео',
                    width=79,
                    height=1,
                    bg='#003366',
                    activebackground='#6699CC',
                    font=('Arial', 10, 'bold'),
                    foreground='#ffff00',
                    activeforeground='#0000ff',
                    command=download_cmd)
    rez_dict['btnDownload'] = btnDownload
    btnDownload.place(x=10, y=240)

    return rez_dict


def clear_prev_info():
    thumbnail_default = tkPhotoImage(file='thumbnail.png')
    dict_mywnd['prev_img'].image = thumbnail_default
    dict_mywnd['prev_img'].config(image=thumbnail_default, width=320, height=190)
    dict_mywnd['info_img'].config(state='normal')
    dict_mywnd['info_img'].delete("1.0", "100.0")
    dict_mywnd['info_img'].config(state='disabled')


def set_thumbnail(thumbnail_url, thumbnail_lbl):
    global bCheck
    response = get_url(thumbnail_url)
    if response.status_code!=200:
        thumbnail_lbl['text'] = 'image not found'
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
    info_img_txt.insert("1.0", 'Title: ' + oYT.title + '\n')
    info_img_txt.insert("2.0", 'Autor: ' + oYT.author + '\n')
    info_img_txt.insert("3.0", 'Publish date: ' + str(oYT.publish_date) + '\n')
    info_img_txt.insert("4.0", 'Video length: ' + str(h) + ' h ' + str(m) + ' m ' + str(s) + ' s')
    info_img_txt.config(state='disabled')


def get_yt(yt_url):
    return YouTube(yt_url, on_progress_callback=on_progress)


def download_cmd():
    if bCheck:
        file_name = ''
        #download_file(yt, file_name)
        clear_prev_info()
    else:
        print('Сначала проверьте скачиваемое видео.')


def download_file(oYT, file_name):
    oYT.streams.get_highest_resolution().download(file_name)


def check_cmd():
    global yt
    clear_prev_info()
    yt = get_yt(dict_mywnd['yt_url'].get())
    set_thumbnail(yt.thumbnail_url, dict_mywnd['prev_img'])
    set_info_img(yt, dict_mywnd['info_img'])


def main_cons():
    download_file(get_yt(input('Введите ссылку youtube: ')), input('Введите имя файла: '))
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

