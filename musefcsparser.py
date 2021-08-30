# -*- coding: utf-8 -*-
# pylint: disable=C0325
# pylint: disable=C0103
# pylint: disable=R1710

"""
@author = Ivan Pokrovac
pylint global evaluation = 9.76/10
"""
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None


def extract_cell_number(path):
    """
    Extracts the number of cells in a sample from .CSV file

    Returns it as a Dictionary
    """

    #Check for extension
    if path[-4:]!=".CSV":
        _csvpath=path[:-4]+".CSV"
    else:
        _csvpath=path
    #Read the lines
    _buf=open(_csvpath)
    lines=_buf.readlines()
    _buf.close()
    #Remove excess
    while "," not in lines[0]:
        lines.pop(0)
    lines.pop(0)
    hcols=lines[0].split(",")
    lines.pop(0)

    #Extract as DataFrame
    df=pd.DataFrame([line.split(", ") for line in lines],columns=hcols)
    df.columns = map(str.strip, df.columns)
    df=df[["Sample ID","Cells/µL"]]
    df.columns=["Sample","Cells"]
    df.Cells=df.Cells.astype(float)

    #Parse as dictionary
    dic=pd.Series(df.Cells.values,index=df.Sample).to_dict()
    return(dic)



class MuseFCSCreator():
    """
    Documentation
    """

    def __init__(self):
        self.samples = None
        self.data = None
        self.meta = None
        self.channel_names = None
        self.header = None
        self.text = None
        self.meta_information = None

    def read_all_headers(self, buf):
        """
        This functions reads all headers in a given .fcs file

        Information that headers extract is:

         [1] Where TEXT begins (byte)

         [2] How long TEXT is (byte)

         [3] Where DATA begins (byte)

         [4] How long DATA is (byte)


        This information is then stored in pandas DataFrame structure

        Parameters
        ----------
        buf : a buffer like data opened in read binary mode.

        Returns
        -------
        Pandas DataFrame n x 4 where columns are where TEXT begins, how long it is, where
        DATA begins, how long is it
        This dataframe is fed into "self.header" attribute

        """

        def header_read(buf, begin=0):
            """
            This function reads from a single header in a given .fcs file
            Values of header are recorded in a list "listvar"
            Position of next header is extracted by looking at where DATA ends
            and adding +1 to that

            Parameters
            ----------
            buf : a buffer like data opened in read binary mode
            begin : byte offset. The default is 0.

            Returns
            -------
            Next offset - position of a next header
            List of [TEXT BEGIN, TEXT SIZE, DATA BEGIN, DATA SIZE] in bytes
            """
            buf.seek(begin)  # starting at the given offset
            stringvar = str(buf.read(56))  # reading header
            listvar = stringvar.split()  # spliting header
            listvar.pop(0)  # first element of header is "FCS" and it's useless
            while len(listvar) > 4:  # listvar needs only 4 elements, and elements are removed from
                listvar.pop()  # the tail until list is 4 elements long
            # offsets are converted into string
            listvar = [int(x) for x in listvar]
            next_offset = listvar[-1]+1  # next offset is calculated
            text_begin = listvar[0]
            # the difference of BEGIN and END gives size-1
            text_size = listvar[1]-listvar[0]
            data_begin = listvar[2]
            # the difference of BEGIN and END gives size-1
            data_size = listvar[3]-listvar[2]
            listvar = [text_begin, text_size, data_begin, data_size]
            return(next_offset, listvar)
        n = 0
        offsets = [n]
        list_of_lists = []

        while True:  # this loop ensures that entire .fcs file is read
            try:
                # begining of the .fcs is 0 bytes
                next_off, listvar = header_read(buf, n)
                n = next_off+n  # offsets are summed together
                offsets.append(n)  # and put in a list
                list_of_lists.append(listvar)
            except ValueError:
                break  # ends the loop

        header = pd.DataFrame(list_of_lists, columns=[
                              "text begin", "text size", "data begin", "data size"])  # header is loaded into dataframe
        offsets.pop()  # last offset is removed, as it is unnecessary
        offsets = np.array(offsets)
        # adding offsets to begin is necessary because
        header["text begin"] = header["text begin"]+offsets
        # MUSE does not have proper $NEXTDATA start
        header["data begin"] = header["data begin"]+offsets
        self.header = header

    def read_texts(self, buf):
        """
        This function creates a dataframe that contains all TEXT data
        Dataframe is of shape N x M where N is number of samples, and M is the number of TEXT parts
        Parameters
        ----------
        buf : a buffer like data opened in read binary mode

        Returns
        -------
        Dataframe of shape N x M where N is number of samples, and M is the number of TEXT parts.
        Dataframe is fed into "self.text" attribute
        """

        def dictionary_make(textstring, delimiter_text="/"):
            """
            Creates a proper dictionary of TEXT part of .fcs file

            Parameters
            ----------
            textstring : string of type b'TEXT' that is split .
            delimiter_text : TYPE, splitter
                DESCRIPTION. The default is "/".

            Returns
            -------
            None.

            """
            first_list = textstring.split(delimiter_text)
            first_list.pop(0)  # remove b'
            first_list.pop()  # remove '
            n = 0
            dic = {}
            while n < len(first_list):
                key = first_list[n]
                n = n+1
                value = first_list[n]
                n = n+1
                dic[key] = value
            return(dic)

        # FIRST CRITICAL POINT
        header = self.header
        dic_list = []
        begins = header["text begin"]  # where TEXTs begin
        sizes = header["text size"]  # how long they are
        for i in range(len(begins)):
            begin = begins[i]
            size = sizes[i]+1
            buf.seek(begin)
            textstring = str(buf.read(size))
            dic_list.append(dictionary_make(textstring))
        textdf = pd.DataFrame(dic_list)  # textdf is made from dictionary list
        textdf["$BEGINDATA"] = header["data begin"]
        textdf["$DATASIZE"] = header["data size"]
        self.text = textdf

        # this complicated line gets the names of channels for the dataset
        ch_names = [str(list(dict.fromkeys((textdf["$P"+str(i)+"S"])))[0])
                    for i in range(1, int(list(dict.fromkeys((textdf["$PAR"])))[0])+1)]
        self.channel_names = ch_names

    def read_data(self, buf):
        """
        This function reads data from DATA segment of .FCS file
        For it to work, it needs to have the name of all the channels
        Number of parameters recorded "$PAR"
        And total number of events "$TOT" recorded for each dataset
        All of that information is given in TEXT
        Therefore it's paramount that TEXT is read first'

        Parameters
        ----------
        buf : a buffer like data opened in read binary mode.

        Returns
        -------
        Dataframe of shape (N x TOT(N)) x PAR+1 where N is the number of samples
        TOT(N) number of events recorded per sample, and PAR is the number of parameters recorded
        First column of the Dataframe is titled "Sample" and it
        contains what sample is the data point from
        this dataframe is fed into "self.data" attribute
        """

        # SECOND CRITICAL POINT
        textdf = self.text
        names = self.channel_names

        relevant = textdf[["GTI$SAMPLEID", "$BEGINDATA", "$DATASIZE"]]
        relevant["$PAR"] = textdf["$PAR"].astype(int)
        relevant["$TOT"] = textdf["$TOT"].astype(int)
        segment_storage = []
        for i in range(len(relevant)):
            buf.seek(relevant["$BEGINDATA"][i])
            segment = buf.read(relevant["$DATASIZE"][i]+1)
            # THIS IS THE MOST IMPORTANT PART
            segment_value = np.frombuffer(segment, dtype=np.float32)
            # reshaping the array into proper form
            segment_value = segment_value.reshape(
                (relevant["$TOT"][i], relevant["$PAR"][i]))
            segment_frame = pd.DataFrame(data=segment_value, columns=names)
            segment_frame.insert(0, "Sample", relevant["GTI$SAMPLEID"][i])
            segment_storage.append(segment_frame)
        data = pd.concat(segment_storage)
        
        self.data = data
        self.data.reset_index(inplace=True,drop=True)
        self.samples = list(relevant["GTI$SAMPLEID"])

    def fix_metadata(self, buf):
        """
        This function simply fixes metadata in a digestible dictionary form
        Information about differences in sample is found in "#SAMPLE INFORMATION"
        and log of events that MUSE records is found in "#LOG OF EVENTS"

        Parameters
        ----------
        buf : a buffer like data opened in read binary mode.

        Returns
        -------
        Dictionary of meta information
        This dictionary is fed in "self.meta_information" attribute

        """
        meta_df = self.text.copy(deep=True)
        together_dic = {}
        for column in meta_df.columns:
            if len(set(meta_df[column])) == 1 or np.sum(meta_df[column].isna()) > 0:
                together_dic[column] = meta_df[column][0]
                meta_df.drop(column, axis=1, inplace=True)

        together_dic["#SAMPLE INFORMATION"] = meta_df
        beglog = int(together_dic["GTI$BEGINLOG"])
        endlog = int(together_dic["GTI$ENDLOG"])
        buf.seek(beglog)
        log = [str(x) for x in buf.read(endlog).splitlines()]
        together_dic["#LOG OF EVENTS"] = log
        self.meta_information = together_dic
        self.meta=self.text
        return()

    def unify_channel_names(self):
        """
        This functions makes sure that all channel names are uniformly named
        MUSE assay changes the names of channels, but ultimately all channels are the same
        FSC-HLin, FSC-HLog, RED-HLin, RED-HLog, YEL-HLin, YEL-HLog, FSC-W
        as well as Time

        Returns
        -------
        Modifies the self.data segment of object, as well as updating channel_names attribute

        """
        channel_dic = {}

        for item in self.channel_names:
            channel_dic[item] = item[item.find("(")+1: item.find(")")]
            if item == "Time":
                channel_dic[item] = item

        self.channel_names = [channel_dic[item] for item in self.channel_names]
        self.data.rename(channel_dic, inplace=True, axis="columns")

    def name_dataset_from_path(self, path):
        """
        This function inserts a column titled "Name" into dataset
        Default value of this title is the name of .FCS file being read


        Parameters
        ----------
        path : .FCS file location.

        Returns
        -------
        Modifies self.data segment of object, inserting "Name" column

        """
        elements = path.split("/")
        while len(elements[-1]) == 0:
            elements.pop()
        data_name = elements[-1]
        self.data.insert(0, "Name", data_name)
        return(data_name)

    def operate(self, path):
        """
        Executes all the methods in the class
        After execution, class has attributes .data and .meta
        """
        buf = open(path, "rb")
        self.read_all_headers(buf)
        self.read_texts(buf)
        self.read_data(buf)
        self.fix_metadata(buf)
        buf.close()
        
        self.unify_channel_names()
        self.name_dataset_from_path(path)
        #Adds another column - number of cells per microliter 
        dic=extract_cell_number(path)
        self.data["Cell Number"]=self.data["Sample"].map(dic)

# END


def parse(path, what="data"):
    """
    Parses .FCS file from a given path

    Parameters
    ----------
    path : path to the .FCS file.
    what : What is returned :
        "data" -> just data
        "full" -> meta, data
        "obj" ->museparser object
        ".

    """
    creat = MuseFCSCreator()
    creat.operate(path)
    if what == "data":
        return(creat.data)
    if what == "full":
        return((creat.meta, creat.data))
    if what == "obj":
        return(creat)


def text_explanation(path):
    """
    From .TXT file (must be named the same as .FCS file, minus the extension) that contains
    explanation for each sample entry

    Parameters
    ----------
    path : Location of .FCS file
    Returns
    -------
    .FCS data with Sample, Replicate, and Name columns according to the .TXT file

    """
    text_path = path.replace(".FCS", ".txt")
    file = open(text_path, "r")
    lines = file.read().splitlines()
    ts_dic = {}
    new_lines = []
    for item in lines:
        if item not in ts_dic.keys():
            ts_dic[item] = 1
            line = item+":"+str(ts_dic[item])
        else:
            ts_dic[item] = ts_dic[item]+1
            line = item+":"+str(ts_dic[item])
        new_lines.append(line)
    file.close()
    sample_lines = lines
    replicate_lines = new_lines

    data = parse(path)
    keys = keys = list(dict.fromkeys(data["Sample"]))

    sample_dictionary = dict(zip(keys, sample_lines))
    replicate_dictionary = dict(zip(keys, replicate_lines))

    data["Replicate"] = data["Sample"].map(replicate_dictionary)
    data["Sample"] = data["Sample"].map(sample_dictionary)
    return(data)
