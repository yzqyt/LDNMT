#!/usr/bin/python
import re
import logging
import os

"""
unused, we have removed all the preprocess function into ldtagger.py
"""






input_file = "test/input.zh"
output_file = "test/output.zh"
word_list = []
tag_list = []

#convert sentence to list
def sentence2list(in_sent):

        searchObj = re.search(r'(\S*)(\t*)([a-z][A-Z]*)', in_sent)  # get match by re
        if searchObj:
            word = "".join(searchObj.group(1))  # get word
            pos_tag = "".join(searchObj.group(3))  # get tag
            if word != "" and pos_tag != "":
                word_list.append(word)
                tag_list.append(pos_tag)
            else:
                raise Exception("require word or tag!")
        else:
            blankObj = re.search(r'(\s*)', in_sent)
            if blankObj:
                pass
            else:
                raise Exception("input sentence format error!")

#convert file to list
def file2list(in_file):

    if not os.path.isfile(in_file):
        raise Exception("input file not found")

    else:
        with open(in_file, 'r', encoding='utf8') as in_stream:
                for sent in in_stream:
                    searchObj = re.search(r'(\S*)(\t*)([a-z][A-Z]*)', sent)  # get match by re
                    if searchObj:
                        word = "".join(searchObj.group(1))  # get word
                        pos_tag = "".join(searchObj.group(3))  # get tag
                        if word != "" and pos_tag != "":
                            word_list.append(word)
                            tag_list.append(pos_tag)
                        else:
                            word_list.append("SEP")
                            tag_list.append("SEP")
                    else:
                        blankObj = re.search(r'(\s*)', sent)
                        if blankObj:
                            word_list.append("SEP")
                            tag_list.append("SEP")
                        else:
                            raise Exception("require word or tag!")


#convert a+uj tag to a
def zh_preprocess(in_file, out_file):

    if not os.path.isfile(in_file):
        raise Exception("input file not found")

    else:
        file2list(in_file)
        for i, tag in enumerate(tag_list):
            # process irrelevant tags
            if tag not in ['n', 'ng', 'nr', 'nrfg', 'nrt', 'ns', 'nt', 'nz', 'v', 'vd',
                           'vg', 'vi', 'vn', 'vq', 'a', 'd', 'SEP']:
                tag_list[i] = "NUL"

            # present all nouns as 'n'
            if tag in ['ng', 'nr', 'nrfg', 'nrt', 'ns', 'nt', 'nz']:
                tag_list[i] = "n"

            # present all verbs as 'v'
            if tag in ['v', 'vd', 'vg', 'vi', 'vn', 'vq']:
                tag_list[i] = "v"

            # process adjective and auxiliary
            if tag == "a" and tag_list[i+1] == "uj":
                word_list[i] = word_list[i] + word_list[i+1] #concatenate
                del tag_list[i+1]  # remove tag "uj"
                del word_list[i+1]  # remove auxiliary words corresponding to "uj" tag

        with open(out_file, 'w', encoding='utf8') as out_stream:
            for i, value in enumerate(tag_list):
                out_stream.write("".join(word_list[i]) + "\t" + value + "\n")  # save to file
                out_stream.flush()

zh_preprocess(input_file, output_file)

# if __name__ == "__main__":
#     logger = logging.getLogger('main')
#     preprocess(input_file, output_file)
#
#     exit(0)

