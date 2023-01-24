"""
    Extracts video and audio files from a given pdf file and save it to the specified output folder.
    :param fname: The name of the pdf file and the path if necesary.
    :param output: The output folder to save the extracted files.
"""
import sys
import pathlib
import fitz

def getmedia(fname,output):
    
    doc = fitz.open(fname)  # opepyn PDF

    for page_num in range(doc.page_count):
        page = doc[page_num]   # load desired page (0-based)
        for annot in page.annots():
            if annot.type[0] != fitz.PDF_ANNOT_RICH_MEDIA:
                continue
            cont = doc.xref_get_key(annot.xref, "RichMediaContent/Assets/Names")
            if cont[0] != "array":  # should be PDF array
                
                sys.exit("unexpected: RichMediaContent/Assets/Names is no array")
            array = cont[1][1:-1]  # remove array delimiters
            # jump over the name / title: we will get it later
            if array[0] == "(":
                i = array.find(")")
            else:
                i = array.find(">")
            xref = array[i + 1 :]  # here is the xref of the actual video stream
            if not xref.endswith(" 0 R"):
                print('error2')
                sys.exit("media contents array has more than one entry")
            xref = int(xref[:-4])  # xref of video stream file
            media_filename = doc.xref_get_key(xref, "F")[1]
            media_xref = doc.xref_get_key(xref, "EF/F")[1]
            media_xref = int(media_xref.split()[0])
            media_stream = doc.xref_stream_raw(media_xref)
            pathlib.Path(f'{output}/{media_filename}').write_bytes(media_stream)
            
if __name__ == '__main__':
    fname=input('name of file: ')
    output=input('output folder: ')
    getmedia(fname,output)
