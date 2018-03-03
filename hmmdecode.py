import math
import sys
import time
import codecs


def get_probability_parameters():
    global initial_transition_probability, transition_probability, last_transition_probability, emission_probability, tags_count
    file = codecs.open('hmmmodel.txt', 'r', encoding='utf-8')
    line_no = 0
    for line in file:
        if line_no == 0:
            initial_transition_probability = eval(line)
        elif line_no == 1:
            transition_probability = eval(line)
        elif line_no == 2:
            last_transition_probability = eval(line)
        elif line_no == 3:
            emission_probability = eval(line)
        elif line_no == 4:
            tags_count = eval(line)

        line_no += 1


def calculate_initial_transition_states():
    global possible_transitions, sequence
    first_word = words[0]
    transition_list = list()
    if first_word in emission_probability:
        for initial_tags in emission_probability[first_word]:
            probability = math.log(initial_transition_probability[initial_tags]) +\
                          math.log(emission_probability[first_word][initial_tags])
            initial_transition = ["q0", initial_tags, first_word, probability]
            possible_transitions.append(initial_transition)
            if first_word not in sequence:
                sequence["1"] = []
                transition_list.append(initial_transition)
            else:
                transition_list.append(initial_transition)
        sequence["1"] = transition_list
    else:
        transition_list = list()
        for initial_tags in initial_transition_probability:
            probability = math.log(initial_transition_probability[initial_tags])
            initial_transition = ["q0", initial_tags, first_word, probability]
            possible_transitions.append(initial_transition)
            if first_word not in sequence:
                sequence["1"] = []
                transition_list.append(initial_transition)
            else:
                transition_list.append(initial_transition)
        sequence["1"] = transition_list


def find_maximum_transition():
    for current_tags in incoming_transitions:
        max_probability = float('-inf')
        for previous_state in incoming_transitions[current_tags]:
            if previous_state[1] > max_probability:
                max_probability = previous_state[1]
                max_state = previous_state

        max_transition = [max_state[0], current_tags, max_state[2], max_probability]

        possible_transitions.append(max_transition)
        seq = str(sequence_no + 1)
        if seq not in sequence:
            sequence[seq] = []
            sequence[seq].append(max_transition)
        else:
            sequence[seq].append(max_transition)


def find_end_maximum_transition():
    for current_tags in end_transitions:
        max_probability = float('-inf')
        for previous_state in end_transitions[current_tags]:
            if previous_state[1] > max_probability:
                max_probability = previous_state[1]
                max_state = previous_state

        max_transition = [max_state[0], current_tags, max_state[2], max_probability]

        possible_transitions.append(max_transition)
        seq = str(sequence_no + 1)
        if seq not in sequence:
            sequence[seq] = []
            sequence[seq].append(max_transition)
        else:
            sequence[seq].append(max_transition)


def get_sequence_using_back_pointers():
    max_probability = float('-inf')
    max_probability_transition = []
    final_sequence = []
    for transition in possible_transitions:
        if transition[3] >= max_probability:
            max_probability = transition[3]
            max_probability_transition = transition

    j = len(words)
    final_sequence.append(max_probability_transition[1])

    for i in range(len(words)):
        from_state = max_probability_transition[0]
        for states in sequence[str(j)]:
            if states[1] == from_state:
                max_probability_transition = states
                final_sequence.append(max_probability_transition[1])
                break
        j -= 1
    final_sequence = final_sequence[::-1]
    return final_sequence


def get_sentence():
    j = 0
    sentence = ""
    for word in words:
        sentence += word + "/" + final_sequence[j] + " "
        j += 1
    sentence = sentence.rstrip()
    return sentence


'''Main'''
startTime = time.time()
initial_transition_probability = dict()
transition_probability = dict()
last_transition_probability = dict()
emission_probability = dict()
tags_count = dict()

get_probability_parameters()

raw_data = codecs.open('zh_dev_raw.txt', 'r', encoding='utf-8')
lines = raw_data.readlines()
possible_transitions = []
incoming_transitions = {}
sequence = {}

hmm_output_file = codecs.open('hmmoutput.txt', 'w', encoding='utf-8')

for line_count in range(len(lines)):
    words = lines[line_count].rstrip().split(" ")

    calculate_initial_transition_states()

    sequence_no = 1

    while sequence_no != len(words):
        incoming_transitions = {}
        for i in range(len(possible_transitions)):
            transitions = possible_transitions.pop(0)
            previous_probability = transitions[3]
            from_tag = transitions[1]
            current_word = words[sequence_no]
            if current_word in emission_probability:
                for tags in emission_probability[current_word]:
                    transition_from_to_tag = from_tag + "->" + tags
                    if tags not in incoming_transitions:
                        incoming_transitions[tags] = []
                    transitions = []
                    current_word_probability = math.log(transition_probability[transition_from_to_tag]) + \
                                               math.log(emission_probability[current_word][tags]) + previous_probability
                    transitions = [from_tag, current_word_probability, current_word]
                    incoming_transitions[tags].append(transitions)
            else:
                for tags in tags_count:
                    transition_from_to_tag = from_tag + "->" + tags
                    if tags not in incoming_transitions:
                        incoming_transitions[tags] = []
                    transitions = []
                    current_word_probability = math.log(transition_probability[transition_from_to_tag]) + previous_probability
                    transitions = [from_tag, current_word_probability, current_word]
                    incoming_transitions[tags].append(transitions)
        find_maximum_transition()
        sequence_no += 1

    end_transitions = dict()
    end_transitions["end"] = []

    for i in range(len(possible_transitions)):
        transitions = possible_transitions.pop(0)
        previous_probability = transitions[3]
        from_tag = transitions[1]
        transitions = []
        end_probability = math.log(last_transition_probability[from_tag]) + previous_probability
        transitions = [from_tag, end_probability, "end"]
        end_transitions["end"].append(transitions)

    find_end_maximum_transition()

    final_sequence = get_sequence_using_back_pointers()

    hmm_output_file.write(get_sentence())
    hmm_output_file.write("\n")

    sequence = {}
    incoming_transitions = {}
    possible_transitions = []

hmm_output_file.close()
endTime = time.time()

print endTime-startTime