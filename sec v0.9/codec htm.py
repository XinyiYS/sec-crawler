# import win32com.client as win32
# ms_word = win32.Dispatch('Word.Application')
# ms_doc  = ms_word.Documents.Add('your_website.html')
# ms_doc.SaveAs('your_word_doc.doc')
# ms_doc.Close()
# ms_word.Quit()


with open("alpha.htm", "rb") as f:
    text= f.read()
# print(text)
import html2text

print(html2text.html2text(str(text)))


