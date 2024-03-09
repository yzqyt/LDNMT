import re
import logging
import os

zh_input_file = "test/input.zh"
zh_output_file = "test/output.zh"
vi_input_file = "test/input.vi"
vi_output_file = "test/output.vi"

zh_word_list = []
zh_tag_list = []
zh_sifted_tag_list = []

vi_word_list = []
vi_tag_list = []
vi_sifted_tag_list = []

zh_sub_file_count = 0
vi_sub_file_count = 0
max_match = False


# language differences tagging, only retain the tags that present the language differences,
# such as: d-a-n in Chinese and corresponding tags R-A-N in Vietnamese
def ldtag():
    global zh_word_list
    global vi_word_list
    global zh_tag_list
    global vi_tag_list
    i = 0

    while i < zh_sub_file_count:
        zh_word_list = []
        vi_word_list = []
        zh_tag_list = []
        vi_tag_list = []
        i = i + 1

        with open("test/input" + str(i) + ".zh", 'r', encoding='utf8') as zh_in_stream:
            with open("test/input" + str(i) + ".vi", 'r', encoding='utf8') as vi_in_stream:
                for zh_line in zh_in_stream:
                    line2list(zh_line, "zh")
                for vi_line in vi_in_stream:
                    line2list(vi_line, "vi")

                #if line in ['\n', '\r\n'] or line.strip() == "": #blank line (end of a sentence)
                zh_noun_block_proc()
                vi_noun_block_proc()
                if noun_match():
                    write_file()
                else:
                    zh_adj_block_proc()
                    vi_adj_block_proc()
                    if adj_match():
                        write_file()
                    else:
                        zh_verb_block_proc()
                        vi_verb_block_proc()
                        if verb_match():
                            write_file()


#<editor-fold desc="match functions">

# find whether noun block are matched
def noun_match():
    if get_non_empty_len(zh_sifted_tag_list) and get_non_empty_len(vi_sifted_tag_list):  # not empty
        zh_tmp_list = list(filter(None, zh_sifted_tag_list))
        vi_tmp_list = list(filter(None, vi_sifted_tag_list))

        for i in range(len(zh_tmp_list)):
            if zh_tmp_list[i] == "n":
                zh_tmp_list[i] = "N"
            if zh_tmp_list[i] == "a":
                zh_tmp_list[i] = "A"
            if zh_tmp_list[i] == "d":
                zh_tmp_list[i] = "R"

        zh_str = "".join(zh_tmp_list)
        vi_tmp_list.reverse()
        vi_str = "".join(vi_tmp_list)

        if zh_str == vi_str:
            return True

    return False

# find whether adj block are matched
def adj_match():
    if get_non_empty_len(zh_sifted_tag_list) and get_non_empty_len(vi_sifted_tag_list):  # not empty
        zh_tmp_list = list(filter(None, zh_sifted_tag_list))
        vi_tmp_list = list(filter(None, vi_sifted_tag_list))

        for i in range(len(zh_tmp_list)):
            if zh_tmp_list[i] == "a":
                zh_tmp_list[i] = "A"
            if zh_tmp_list[i] == "d":
                zh_tmp_list[i] = "R"

        zh_str = "".join(zh_tmp_list)
        vi_tmp_list.reverse()  # reverse
        vi_str = "".join(vi_tmp_list)

        if zh_str == vi_str:
            return True

    return False


# find whether verb block are matched
def verb_match():
    print("in verb match")
    if get_non_empty_len(zh_sifted_tag_list) and get_non_empty_len(vi_sifted_tag_list):  # not empty
        zh_tmp_list = list(filter(None, zh_sifted_tag_list))  # remove ""
        vi_tmp_list = list(filter(None, vi_sifted_tag_list))

        for i in range(len(zh_tmp_list)):
            if zh_tmp_list[i] == "v":
                zh_tmp_list[i] = "V"
            if zh_tmp_list[i] == "d":
                zh_tmp_list[i] = "R"

        zh_str = "".join(zh_tmp_list)
        vi_tmp_list.reverse()  # reverse
        vi_str = "".join(vi_tmp_list)

        if zh_str == vi_str:
            return True

    return False

#</editor-fold>


#<editor-fold desc="noun, adj and verb block recognize and process functions">

# recognize zh noun block(tags:d-a-n or a...a-n)
def zh_noun_block_proc():
    global zh_sifted_tag_list
    zh_format_tag()  # preprocess zh list
    zh_sifted_tag_list = [''] * len(zh_tag_list)

    # tag process
    for i, tag in enumerate(zh_tag_list):
        j = i - 1
        if tag == 'n':
            while j >= 0:
                if zh_tag_list[j] == 'a':
                    zh_sifted_tag_list[i] = 'n'
                    zh_sifted_tag_list[j] = 'a'
                    j = j - 1
                else:
                    if zh_tag_list[j] == 'd':
                        if j == (i-1):
                            return [] # incorrect pos tag
                        if zh_tag_list[j+1] == 'a' and zh_tag_list[j-1] not in ['a', 'd']:
                            zh_sifted_tag_list[j] = 'd'
                            j = j - 1
                        else:
                            return [] # incorrect pos tag
                    else:
                        break
        # greedy match: get min matched result
        if not max_match and len(list(filter(None, zh_sifted_tag_list))):
            break

    return zh_sifted_tag_list

# recognize vi noun block(tags: N-A-R or N -A ... A)
def vi_noun_block_proc():
    global vi_sifted_tag_list
    vi_format_tag()  # preprocess vi list
    vi_sifted_tag_list = [''] * len(vi_tag_list)

    #tag process
    for i, tag in enumerate(vi_tag_list):
        j = i + 1
        if tag == 'N' and j < len(vi_tag_list):
            while j < len(vi_tag_list):
                if vi_tag_list[j] == 'A':
                    vi_sifted_tag_list[i] = 'N'
                    vi_sifted_tag_list[j] = 'A'
                    j = j + 1
                else:
                    if vi_tag_list[j] == 'R':
                        if j == (i+1):
                            return []
                        if vi_tag_list[j-1] == 'A':
                            if j + 1 == len(vi_tag_list) or vi_tag_list[j+1] not in ['A', 'R']:
                                vi_sifted_tag_list[j] = 'R'
                                j = j + 1
                        else:
                            return []
                    else:
                        break
        # greedy match: get min matched result
        if not max_match and len(list(filter(None, vi_sifted_tag_list))):
            break

    return vi_sifted_tag_list


# recognize zh adj block(tags:d-a or d-a...a)
def zh_adj_block_proc():
    global zh_sifted_tag_list
    zh_format_tag()  # preprocess zh list
    zh_sifted_tag_list = [''] * len(zh_tag_list)

    # tag process
    for i, tag in enumerate(zh_tag_list):
        j = i - 1
        if tag == 'a':
            while j >= 0:
                if zh_tag_list[j] == 'd':
                    zh_sifted_tag_list[i] = 'a'
                    zh_sifted_tag_list[j] = 'd'
                    j = j - 1

        # greedy match: get min matched result
        if not max_match and len(list(filter(None, zh_sifted_tag_list))):
            break

    return zh_sifted_tag_list


# recognize vi adj block(tags: A-R or A...A-R)
def vi_adj_block_proc():
    global vi_sifted_tag_list
    vi_format_tag()  # preprocess vi list
    vi_sifted_tag_list = [''] * len(vi_tag_list)

    #tag process
    for i, tag in enumerate(vi_tag_list):
        j = i + 1
        if tag == 'A' and j < len(vi_tag_list):
            while j < len(vi_tag_list):
                if vi_tag_list[j] == 'R':
                    vi_sifted_tag_list[i] = 'A'
                    vi_sifted_tag_list[j] = 'R'
                    j = j + 1

        # greedy match: get min matched result
        if not max_match and len(list(filter(None, vi_sifted_tag_list))):
            break

    return vi_sifted_tag_list


# recognize zh verb block(tags:a-v or a-a...v)
def zh_verb_block_proc():
    global zh_sifted_tag_list
    zh_format_tag()  # preprocess zh list
    zh_sifted_tag_list = [''] * len(zh_tag_list)

    # tag process
    for i, tag in enumerate(zh_tag_list):
        j = i - 1
        if tag == 'v':
            while j >= 0:
                if zh_tag_list[j] == 'd':
                    zh_sifted_tag_list[i] = 'v'
                    zh_sifted_tag_list[j] = 'd'
                    j = j - 1

        # greedy match: get min matched result
        if not max_match and len(list(filter(None, zh_sifted_tag_list))):
            break

    return zh_sifted_tag_list


# recognize vi adj block(tags: A-R or A...A-R)
def vi_verb_block_proc():
    global vi_sifted_tag_list
    vi_format_tag()  # preprocess vi list
    vi_sifted_tag_list = [''] * len(vi_tag_list)

    # tag process
    for i, tag in enumerate(vi_tag_list):
        j = i + 1
        if tag == 'V' and j < len(vi_tag_list):
            while j < len(vi_tag_list):
                if vi_tag_list[j] == 'R':
                    vi_sifted_tag_list[i] = 'V'
                    vi_sifted_tag_list[j] = 'R'
                    j = j + 1

        # greedy match: get min matched result
        if not max_match and len(list(filter(None, vi_sifted_tag_list))):
            break

    return vi_sifted_tag_list

#</editor-fold>

#<editor-fold desc="preprocess functions">

# zh preprocess
def zh_format_tag():

    for i, tag in enumerate(zh_tag_list):
        # process irrelevant tags
        if tag not in ['n', 'ng', 'nr', 'nrfg', 'nrt', 'ns', 'nt', 'nz', 'r', 'v', 'vd',
                       'vg', 'vi', 'vn', 'vq', 'a', 'd']:
            zh_tag_list[i] = ''

        # present all nouns as 'n'
        if tag in ['ng', 'nr', 'nrfg', 'nrt', 'ns', 'nt', 'nz']:
            zh_tag_list[i] = "n"

        # present all verbs as 'v'
        if tag in ['v', 'vd', 'vg', 'vi', 'vn', 'vq']:
            zh_tag_list[i] = "v"

        # process adjective and auxiliary: convert a+uj tag to a
        if tag == "a" and (i+1) < len(zh_tag_list) and zh_tag_list[i+1] == "uj":
            zh_word_list[i] = zh_word_list[i] + zh_word_list[i+1]  # concatenate
            del zh_tag_list[i+1]  # remove tag "uj"
            del zh_word_list[i+1]  # remove the word corresponding to "uj" tag

# vi preprocess
def vi_format_tag():

    for i, tag in enumerate(vi_tag_list):
        # process irrelevant tags
        if tag not in ['N', 'Np', 'Nc', 'Nu', 'Ny', 'Nb', 'P', 'V', 'Vb', 'A', 'R']:
            vi_tag_list[i] = ''

        # present all nouns as 'n'
        if tag in ['Np', 'Nc', 'Nu', 'Ny', 'Nb']:
            vi_tag_list[i] = "N"

        # present all verbs as 'v'
        if tag == 'Vb':
            vi_tag_list[i] = "V"

        # process adjective and auxiliary: convert a+uj tag to a
        if tag == "N" and (i - 1) > 0 and vi_tag_list[i - 1] == "NC":
            vi_word_list[i] = vi_word_list[i-1] + " " + vi_word_list[i]  # concatenate
            del vi_tag_list[i-1]  # remove tag "NC"
            del vi_word_list[i-1]  # remove the word corresponding to "NC" tag


#</editor-fold>

#<editor-fold desc="util functions">

def zh_file_preprocess():
    global zh_sub_file_count
    with open(zh_input_file, 'r', encoding='utf8') as in_stream:
        tmp_word_list = []
        tmp_tag_list = []
        sub_file_index = 1

        for line in in_stream:
            search_obj = re.search(r'(\S*)(\t*)([a-zA-Z]*)', line)  # get match by re
            if search_obj:
                word = "".join(search_obj.group(1))  # get word
                tag = "".join(search_obj.group(3))  # get pos tag
                if word != "" and tag != "":
                    tmp_word_list.append(word)
                    tmp_tag_list.append(tag)
                else:
                    pass # raise Exception("zh input sentence format error!")

            if line in ['\n', '\r\n'] or line == "":
                with open("test/input" + str(sub_file_index) + ".zh", 'w', encoding='utf8') as out_stream:
                    for i, value in enumerate(tmp_tag_list):
                        out_stream.write(tmp_word_list[i] + "\t" + value + "\n")

                    #out_stream.write("\n")
                    out_stream.flush()  # save to file

                tmp_word_list = []
                tmp_tag_list = []
                zh_sub_file_count += 1
                sub_file_index += 1


def vi_file_preprocess():
    global vi_sub_file_count

    with open(vi_input_file, 'r', encoding='utf8') as in_stream:
        tmp_word_list = []
        tmp_tag_list = []
        sub_file_index = 1

        for line in in_stream:
            search_obj = re.search(r'([0-9]\s)(\S*)(\s*)([a-zA-Z]*)(\s*_)', line)  # get match by re
            if search_obj:
                word = "".join(search_obj.group(2))  # write word
                tag = "".join(search_obj.group(4))  # write tag
                if word != "" and tag != "":
                    tmp_word_list.append(word)
                    tmp_tag_list.append(tag)
                else:
                    raise Exception("vi input sentence format error!")

            if line in ['\n', '\r\n'] or line.strip() == "":
                with open("test/input" + str(sub_file_index) + ".vi", 'w', encoding='utf8') as out_stream:
                    for i, value in enumerate(tmp_tag_list):
                        out_stream.write(tmp_word_list[i] + "\t" + value + "\n")

                    #out_stream.write("\n")
                    out_stream.flush()  # save to file

                tmp_word_list = []
                tmp_tag_list = []
                vi_sub_file_count += 1
                sub_file_index += 1

#</editor-fold>


#<editor-fold desc="util functions">

#convert every sentence in the file to list
def line2list(in_sent, lang):

    search_obj = re.search(r'(\S*)(\t*)([a-zA-Z]*)', in_sent)  # get match by re
    if search_obj:
        word = "".join(search_obj.group(1))  # get word
        tag = "".join(search_obj.group(3))  # get pos tag
        if word != "" and tag != "":
            if lang == "zh":
                zh_word_list.append(word)
                zh_tag_list.append(tag)
            if lang == "vi":
                vi_word_list.append(word)
                vi_tag_list.append(tag)
        else:
            pass
    else:
        blank_obj = re.search(r'(\s*)', in_sent)
        if blank_obj:
            pass
        else:
            raise Exception("input line format error!")


def get_non_empty_len(in_list):
    i = 0
    for value in in_list:
        if value != '':
            i = i + 1
    return i


def write_file():
    with open(zh_output_file, 'a', encoding='utf8') as out_stream:
        zh_sent = ""
        for k, sifted_tag in enumerate(zh_sifted_tag_list):
            if sifted_tag != "":
                sifted_tag = " " + zh_sifted_tag_list[k]  # add word separator(blank)
            zh_sent += " " + zh_word_list[k] + sifted_tag

        out_stream.write(zh_sent.lstrip().rstrip() + "\n")
        out_stream.flush()

    with open(vi_output_file, 'a', encoding='utf8') as out_stream:
        vi_sent = ""
        for k, sifted_tag in enumerate(vi_sifted_tag_list):
            if sifted_tag != "":
                sifted_tag = " " + vi_sifted_tag_list[k]  # add word separator(blank)
            vi_sent += " " + vi_word_list[k] + sifted_tag

        out_stream.write(vi_sent.lstrip().rstrip() + "\n")
        out_stream.flush()

#</editor-fold>


if __name__ == "__main__":
    if zh_sub_file_count == vi_sub_file_count:
        zh_file_preprocess()
        vi_file_preprocess()
    else:
        raise Exception("Inconsistent number of files!")

    ldtag()
    exit(0)
