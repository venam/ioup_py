"""
    ioup.py backend (controler) - upload files to pub.iotek.org


    Copyright (c) 2014, IOTek <patrick (at) iotek (dot) org>


    Permission to use, copy, modify, and/or distribute this software for any
    purpose with or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.

    THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import  urllib2
import  os
import  multipart_encoder
import  random


def usual_header(TOKEN):
    """
    usual_header :: String -> String

    takes the private server token

    return the header that is needed for all requests
    """
    return "token="+TOKEN+"&is_ioup=1"


def check_list(TOKEN):
    """
    want to return a dictionary
    check_list :: String -> String

    takes the private server token

    return a dict of available files on the server in the following form:
    {
        "filename"   : "p/code",
        "filename903": "p/code" #if there are 2 files that have the same name 
                                #it append 3 random numbers
    }

    The character separating the link and the filename is a hard TAB

    returns {"":""} upon error
    """
    try:
        response = urllib2.urlopen("http://pub.iotek.org/p/list.php", data=usual_header(TOKEN)).read()
        if "p/" not in response:
            #there's nothing interesting in the response or something fucked up
            print "nothing found on server"
            return {"":""}
        dico     = {}
        splitted = response.split("\n")
        for uploaded_file in splitted:
            if "\t" in uploaded_file:
                inside = uploaded_file.split("\t")
                dico[inside[1]+" - "+inside[0]] = inside[0]
        return dico
    except Exception, e:
        print e
        return {" ":" "}
    return response;


def remove_file(TOKEN, file_code):
    """
    remove_file :: String -> String -> Bool

    takes the private server token

    takes a file name p/something and remove it from the upstream server
    it returns True upon a successful transation and False on error
    """
    try:
        urllib2.urlopen("http://pub.iotek.org/remove.php", data=usual_header(TOKEN)+"&"+file_code+"=1")
    except Exception,e:
        print e
        return False
    return True

def upload_file(TOKEN, file_to_upload):
    """
    upload_file :: String -> String -> String

    takes the private server token

    takes the absolute location of the file and upload it to the server
    it returns the upload URL
    on failure it returns the " " string
    """
    try:
        extension = os.path.splitext(file_to_upload)[1][1:]
        url       = "http://pub.iotek.org/post.php"
        fields = {'token': TOKEN, 'is_ioup': 1} 
        files = {'pdata': {'filename': file_to_upload, 'content': open(file_to_upload,'rb').read()}}
        data, headers = multipart_encoder.encode_multipart(fields, files)
        response = urllib2.Request('http://pub.iotek.org/post.php', data=data, headers=headers)
        f = urllib2.urlopen(response)
        return f.read()
    except Exception, e:
        print e
        return " "


