import sys
import time
import codecs

def count_initial_tags(lines):
    initial_tags_count = {}
    for line_no in range(len(lines)):
        words = lines[line_no].rstrip().split(" ")
        first_word_tag = words[0][words[0].rfind("/")+1:len(words[0])]
        if first_word_tag in initial_tags_count:
            initial_tags_count[first_word_tag] = initial_tags_count[first_word_tag] + 1
        else:
            initial_tags_count[first_word_tag] = 1
    return initial_tags_count


def count_last_tags(lines):
    last_tags_count = {}
    for line_no in range(len(lines)):
        words = lines[line_no].rstrip().split(" ")
        last_word = words[len(words)-1]
        last_word_tag = last_word[last_word.rfind("/")+1:len(last_word)]
        if last_word_tag in last_tags_count:
            last_tags_count[last_word_tag] = last_tags_count[last_word_tag] + 1
        else:
            last_tags_count[last_word_tag] = 1
    return last_tags_count


def count_all_tags(lines):
    all_tags_count = {}
    for line_no in range(len(lines)):
        words = lines[line_no].rstrip().split(" ")
        for word in words:
            word_tag = word[word.rfind("/")+1:len(word)]
            if word_tag in all_tags_count:
                all_tags_count[word_tag] = all_tags_count[word_tag] + 1
            else:
                all_tags_count[word_tag] = 1
    return all_tags_count


def count_transition_tags(lines):
    global unique_tags_following_from_tag
    transition_tags_count = {}
    for line_no in range(len(lines)):
        words = lines[line_no].rstrip().split(" ")
        for word_count in range(len(words)-1):
            from_tag = words[word_count][words[word_count].rfind("/")+1:len(words[word_count])]
            to_tag = words[word_count+1][words[word_count+1].rfind("/") + 1:len(words[word_count+1])]
            transition_tag = from_tag + "->" + to_tag
            if transition_tag in transition_tags_count:
                transition_tags_count[transition_tag] = transition_tags_count[transition_tag] + 1
            else:
                transition_tags_count[transition_tag] = 1

            if from_tag in unique_tags_following_from_tag:
                if transition_tag not in unique_tags_following_from_tag[from_tag]:
                    unique_tags_following_from_tag[from_tag].append(transition_tag)
            else:
                unique_tags_following_from_tag[from_tag] = []
                unique_tags_following_from_tag[from_tag].append(transition_tag)
    return transition_tags_count


def calculate_initial_transition_probability():
    initial_transition_probability = {}
    for tag in all_tags_count:
        if tag in initial_tags_count:
            initial_transition_probability[tag] = (initial_tags_count[tag] + 1)/(1.0*len(lines) + len(all_tags_count))
        else:
            initial_transition_probability[tag] = 1.0/(len(lines) + len(all_tags_count))
    return initial_transition_probability


def calculate_transition_probability():
    transition_probability = {}
    for from_tag in all_tags_count:
        for to_tag in all_tags_count:
            transition_string = from_tag+"->"+to_tag
            if transition_string in transition_tags_count:
                transition_probability[transition_string] = (transition_tags_count[transition_string] + 1) / (1.0 * all_tags_count[from_tag] + len(all_tags_count))
            else:
                transition_probability[transition_string] = 1.0 / (all_tags_count[from_tag] + len(all_tags_count))

    return transition_probability


def calculate_last_transition_probability():
    last_transition_probability = {}
    for tag in all_tags_count:
        if tag in last_tags_count:
            last_transition_probability[tag] = (last_tags_count[tag] + 1)/(1.0 * all_tags_count[tag] + len(all_tags_count))
        else:
            last_transition_probability[tag] = 1.0/(all_tags_count[tag] + len(all_tags_count))
    return last_transition_probability

'''Emission Probability'''


def count_word_as_tag():
    word_as_tag_count = {}
    for line_no in range(len(lines)):
        words = lines[line_no].rstrip().split(" ")
        for word in words:
            word_without_tag = word[0:word.rfind("/")]
            word_tag = word[word.rfind("/")+1:len(word)]
            if word_without_tag not in word_as_tag_count:
                word_as_tag_count[word_without_tag] = {}
            if word_tag in word_as_tag_count[word_without_tag]:
                word_as_tag_count[word_without_tag][word_tag] = word_as_tag_count[word_without_tag][word_tag] + 1
            else:
                word_as_tag_count[word_without_tag][word_tag] = 1
    return word_as_tag_count


def calculate_emission_probability():
    emission_probability = {}
    for word in word_as_tag_count:
        emission_probability[word] = {}
        for tag in word_as_tag_count[word]:
            emission_probability[word][tag] = word_as_tag_count[word][tag]/(1.0 * all_tags_count[tag])
    return emission_probability


'''Main'''
startTime = time.time()
training_data = codecs.open('zh_train_tagged.txt', 'r', encoding='utf-8')

lines = training_data.readlines()

unique_tags_following_from_tag = {}

initial_tags_count = count_initial_tags(lines)
last_tags_count = count_last_tags(lines)
all_tags_count = count_all_tags(lines)
transition_tags_count = count_transition_tags(lines)
initial_transition_probability = calculate_initial_transition_probability()
transition_probability = calculate_transition_probability()
last_transition_probability = calculate_last_transition_probability()

word_as_tag_count = count_word_as_tag()
emission_probability = calculate_emission_probability()


hmm_model_file = codecs.open("hmmmodel.txt", "w", encoding='utf-8')
hmm_model_file.write(str(initial_transition_probability) + "\n")
hmm_model_file.write(str(transition_probability) + "\n")
hmm_model_file.write(str(last_transition_probability) + "\n")
hmm_model_file.write(str(emission_probability) + "\n")
hmm_model_file.write(str(all_tags_count))
hmm_model_file.close()
endTime = time.time()

print endTime-startTime