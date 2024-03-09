#!/usr/bin/python
import re
import logging
import os

"""
unused, we have removed all the preprocess function into ldtagger.py
"""






input_file = "test/input.vi"
output_file = "test/output.vi"
word_list = []
tag_list = []

#convert sentence to list,
def sentence2list(in_file):

    with open(in_file, 'r', encoding='utf8') as in_stream:
            for sent in in_stream:
                searchObj = re.search(r'([0-9]\s)(\S*)(\s*)([a-z][A-Z]*)(\s*_)', sent)  # get match by re
                if searchObj:
                    word = "".join(searchObj.group(2))  # write word
                    pos_tag = "".join(searchObj.group(4))  # write tag
                    if pos_tag not in ['N', 'Np', 'Nc', 'Nu', 'Ny', 'Nb', 'V', 'Vb', 'A', 'R']:
                        pos_tag = "NUL"
                    if word != "" and pos_tag != "":
                        word_list.append(word)
                        tag_list.append(pos_tag)
                    if word == "" and pos_tag == "":
                        word_list.append("SEP")
                        tag_list.append("SEP")
                else:
                    blankObj = re.search(r'(\s*)', sent)
                    if blankObj:
                        word_list.append("SEP")
                        tag_list.append("SEP")
                    else:
                        raise Exception("require word or tag!")


#convert file to list,
def file2list(in_file):

    if not os.path.isfile(in_file):
        raise Exception("input file not found")

    else:
        with open(in_file, 'r', encoding='utf8') as in_stream:
                for sent in in_stream:
                    searchObj = re.search(r'([0-9]\s)(\S*)(\s*)([a-z][A-Z]*)(\s*_)', sent)  # get match by re
                    if searchObj:
                        word = "".join(searchObj.group(2))  # write word
                        pos_tag = "".join(searchObj.group(4))  # write tag
                        if pos_tag not in ['N', 'Np', 'Nc', 'Nu', 'Ny', 'Nb', 'V', 'Vb', 'A', 'R']:
                            pos_tag = "NUL"
                        if word != "" and pos_tag != "":
                            word_list.append(word)
                            tag_list.append(pos_tag)
                        if word == "" and pos_tag == "":
                            word_list.append("SEP")
                            tag_list.append("SEP")
                    else:
                        blankObj = re.search(r'(\s*)', sent)
                        if blankObj:
                            word_list.append("SEP")
                            tag_list.append("SEP")
                        else:
                            raise Exception("require word or tag!")


def vi_preprocess(in_file, out_file):

    logger = logging.getLogger('vi preprocess')

    if not os.path.isfile(in_file):
        raise Exception("input file not found, %s" % in_file)
    else:
        file2list(in_file)

        with open(out_file, 'w', encoding='utf8') as out_stream:
            for i, value in enumerate(tag_list):
                out_stream.write("".join(word_list[i]) + "\t" + value + "\n")  # save to file
                out_stream.flush()
        # with open(in_file, 'r', encoding='utf8') as in_stream:
        #     with open(out_file, 'w', encoding='utf8') as out_stream:
        #         for sent in in_stream:
        #             searchObj = re.search(r'([0-9]\s)(\S*)(\s*)(\S*)(\s*_)', sent)  # re
        #             if searchObj:
        #                 pos_tag = "".join(searchObj.group(4))
        #                 # if pos_tag not in ['N', 'Np', 'Nc', 'Nu', 'Ny', 'Nb', 'V', 'Vb', 'A', 'R']:
        #                 #     pos_tag = ""
        #                 out_stream.write("".join(searchObj.group(2)) + "\t" + pos_tag + "\n")  # save group 2
        #                 out_stream.flush()
        #             else:
        #                 out_stream.write("\n")

        logger.info("vi preprocess finished.")


vi_preprocess(input_file, output_file)

# if __name__ == "__main__":
#     logger = logging.getLogger('main')
#     preprocess(input_file, output_file)
#
#     exit(0)