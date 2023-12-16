"""Functions related to japanese NLP"""


class Classifier:

    @staticmethod
    def contains_no_parsable_text(input_text: str) -> bool:
        replacement_list = ["「", "」", "―", "！", "？", '『', '』']
        for char in replacement_list:
            input_text = input_text.replace(char, '')

        return len(input_text) < 3
