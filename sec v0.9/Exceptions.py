
class GetUrlException(Exception):
    def __init__(self, htm, errors = 0):
        # Call the base class constructor with the parameters it needs
        super().__init__()
        self.errors = errors
        self.htm = htm
        self.message =  "Error occurred during getting the urls for the documents. Check the filing htm at {}.\n".format(self.htm)


class DownloadException(Exception):
    def __init__(self, htm, filepath, errors = 1):

        super().__init__()
        self.errors = errors
        self.htm = htm
        self.filepath =filepath
        self.message = "Error occurred during fetching documents from SEC. Check the links for individual filings at {}. And check the locations on disk to store the filings at {}.\n".format(self.htm, self.filepath)

class LoggingException(Exception):
    def __init__(self, logpath, errors = 2):

        super().__init__()
        self.errors = errors
        self.logpath= logpath
        self.message = "Error occurred during keeping the download log for filings. Check the location for the logs at {}.\n".format(self.logpath)