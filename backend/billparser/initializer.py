from billparser.db.handler import import_title, get_number
import locale
def getpreferredencoding(do_setlocale = True):
   return "utf-8"
locale.getpreferredencoding = getpreferredencoding

if __name__ == "__main__":
    import os

    files = os.listdir("usc")
    files = [x[3:].split(".")[0] for x in files]
    files = sorted(files, key=lambda x: get_number(x))
    for file in files:
        import_title(file, "Q1-2019")
