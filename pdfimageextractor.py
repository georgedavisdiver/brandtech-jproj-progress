#modified from https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/extract-images/extract.py
"""
Modified version of "Extract images from a PDF document"
Original code Copyright (c) 2018 Jorj X. McKie
Modifications Copyright (c) The Brandtech Group

This code is based on the original code, which is licensed under the GNU GPL v3.
This modified version is also licensed under the GNU GPL v3.

"""



import io
import os
import fitz



def recoverpix(doc, item):
    xref = item[0]  # xref of PDF image
    smask = item[1]  # xref of its /SMask

    # special case: /SMask or /Mask exists
    if smask > 0:
        pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
        if pix0.alpha:  # catch irregular situation
            pix0 = fitz.Pixmap(pix0, 0)  # remove alpha channel
        mask = fitz.Pixmap(doc.extract_image(smask)["image"])

        try:
            pix = fitz.Pixmap(pix0, mask)
        except:  # fallback to original base image in case of problems
            pix = fitz.Pixmap(doc.extract_image(xref)["image"])

        if pix0.n > 3:
            ext = "pam"
        else:
            ext = "png"

        return {  # create dictionary expected by caller
            "ext": ext,
            "colorspace": pix.colorspace.n,
            "image": pix.tobytes(ext),
        }

    # special case: /ColorSpace definition exists
    # to be sure, we convert these cases to RGB PNG images
    if "/ColorSpace" in doc.xref_object(xref, compressed=True):
        pix = fitz.Pixmap(doc, xref)
        pix = fitz.Pixmap(fitz.csRGB, pix)
        return {  # create dictionary expected by caller
            "ext": "png",
            "colorspace": 3,
            "image": pix.tobytes("png"),
        }
    return doc.extract_image(xref)

def extractimages(fname, imgdir):
    doc = fitz.open(fname)

    page_count = doc.page_count  # number of pages

    xreflist = []
    imglist = []
    for page in range(page_count):
        
        il = doc.get_page_images(page)
        imglist.extend([x[0] for x in il])
        for img in il:
            xref = img[0]
            if xref in xreflist:
                continue
            width = img[2]
            height = img[3]

            image = recoverpix(doc, img)
            n = image["colorspace"]
            imgdata = image["image"]

            

            imgfile = os.path.join(imgdir, "img%05i.%s" % (xref, image["ext"]))
            fout = open(imgfile, "wb")
            fout.write(imgdata)
            fout.close()
            xreflist.append(xref)


    imglist = list(set(imglist))
    print(len(set(imglist)), "images in total")
    print(len(xreflist), "images extracted")

    
if __name__ == "__main__":
    fname = input('filename: ')
    output = input('output folder name: ')
    extractimages(fname,output)



