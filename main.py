import os
import sys

from pl_parser import Parser

DEFAULT_INPUT_FILE = "input.txt"


def divide_input(inputs):
    ret = []
    line_no = 0
    n = len(inputs)

    ret.append([])
    while line_no < n:
        line = inputs[line_no]
        # if line is empty then ignore
        if not line:
            line_no = line_no + 1
            continue

        # check number of line
        ret[-1].append(line)
        num_of_lines = int(line.split()[0])
        for _ in range(num_of_lines):
            line_no = line_no + 1
            ret[-1].append(inputs[line_no])
        # proposition
        line_no = line_no + 1
        ret[-1].append(inputs[line_no])

        # take next input if exists
        line_no = line_no + 1
        ret.append([])

    if not ret[-1]:
        ret = ret[:-1]
    return ret


def take_input(hard_input):
    inputs = []

    # check input from file if file exists
    if not hard_input and os.path.isfile(DEFAULT_INPUT_FILE):
        with open(DEFAULT_INPUT_FILE) as f:
            temp_inputs = list(map(lambda x: x.strip(), f.readlines()))
            inputs = divide_input(temp_inputs)
    # otherwise take input from user
    else:
        # first check number of line
        inputs.append([])
        buffer_input = input()
        inputs[0].append(buffer_input)
        try:
            num_of_rows = int(buffer_input.split()[0])
            # take number of line as input
            for _ in range(num_of_rows):
                inputs[0].append(input())
            # now time to add proposition inputs
            inputs[0].append(input())
        except ValueError as e:
            print("Provide number of line as integer")
    return inputs


def run(hard_input=False):
    inputs = take_input(hard_input)
    for obj in inputs:
        pl_problem = Parser(obj).get_parsed_pl_problem()
        print(pl_problem)


if __name__ == "__main__":
    # check command wih -i flag (to take manual input)
    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        run(hard_input=True)
    else:
        run()
