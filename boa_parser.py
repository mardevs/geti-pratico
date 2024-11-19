# Reference: https://py-pdf-parser.readthedocs.io/en/latest/examples/simple_memo.html#step-3-extract-the-data

import re
from py_pdf_parser.loaders import load_file

curriculum_pattern = re.compile(r"\d{4}/\d+")

class BoaInfo:
    def __init__(self, student_name: str, dre: str, course_name: str, situation: str, curriculum: str):
        self.student_name = student_name
        self.dre = dre
        self.course_name = course_name
        self.situation = situation
        self.curriculum = curriculum

def parse_boa(file_path) -> BoaInfo:
    document = load_file(file_path)

    page_1_elements = document.elements.filter_by_page(1)

    student_element = page_1_elements.filter_by_text_equal("ALUNO:").extract_single_element()
    dre_element = page_1_elements.filter_by_text_equal("DRE:").extract_single_element()
    course_element = page_1_elements.filter_by_text_equal("CURSO ATUAL:").extract_single_element()
    situation_element = page_1_elements.filter_by_text_equal("SITUAÇÃO ATUAL:").extract_single_element()

    student_value = page_1_elements.to_the_right_of(student_element).to_the_left_of(course_element).extract_single_element().text()
    dre_value = page_1_elements.to_the_right_of(dre_element).to_the_left_of(situation_element).extract_single_element().text()
    course_value = page_1_elements.to_the_right_of(course_element).extract_single_element().text()
    situation_value = page_1_elements.to_the_right_of(situation_element).extract_single_element().text()

    curriculum_string = page_1_elements.filter_by_text_contains("Versão curricular:").extract_single_element().text()
    curriculum = curriculum_pattern.search(curriculum_string)[0]

    return BoaInfo(student_value, dre_value, course_value, situation_value, curriculum)