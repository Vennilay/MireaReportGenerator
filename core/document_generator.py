"""
Модуль для генерации DOCX документов
"""

import os
from datetime import datetime
from typing import List
from docxtpl import DocxTemplate
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from utils.date_utils import format_date_russian


class DocumentGenerator:
    """
    Генератор DOCX документов
    """

    def __init__(self, template_path: str):
        self.template_path = template_path

    def validate_template(self) -> bool:
        return os.path.exists(self.template_path)

    def generate(
        self,
        group: str,
        student_name: str,
        teacher_name: str,
        work_number: str,
        date: datetime,
        code_files: List[str],
        output_path: str,
    ) -> bool:
        try:
            doc = DocxTemplate(self.template_path)
            context = {
                "group": group,
                "student_name": student_name,
                "teacher_name": teacher_name,
                "work_number": work_number,
                "date": format_date_russian(date),
            }
            doc.render(context)

            temp_file = "temp_output.docx"
            doc.save(temp_file)

            final_doc = Document(temp_file)

            for idx, file_path in enumerate(code_files, 1):
                if idx > 1:
                    final_doc.add_page_break()
                self._add_task_heading(final_doc, idx)
                code_content = self._read_code_file(file_path)
                self._add_code_content(final_doc, code_content)

            final_doc.save(output_path)

            if os.path.exists(temp_file):
                os.remove(temp_file)

            return True
        except Exception as e:
            print(f"Ошибка генерации документа: {str(e)}")
            return False

    @staticmethod
    def _add_task_heading(doc, task_number: int):
        heading = doc.add_paragraph()
        heading.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        heading.paragraph_format.first_line_indent = Cm(1.25)
        heading.paragraph_format.space_before = Pt(0)
        heading.paragraph_format.space_after = Pt(6)

        run = heading.add_run(f"Задание № {task_number}:")
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        run.bold = True

    @staticmethod
    def _read_code_file(file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            return (
                f"[Ошибка чтения файла: {os.path.basename(file_path)}\n"
                f"Причина: {str(e)}]"
            )

    @staticmethod
    def _add_code_content(doc, code_content: str):
        code_para = doc.add_paragraph()
        code_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        code_para.paragraph_format.left_indent = Cm(1.25)
        code_para.paragraph_format.first_line_indent = Cm(0)
        code_para.paragraph_format.space_before = Pt(0)
        code_para.paragraph_format.space_after = Pt(0)
        code_para.paragraph_format.line_spacing = 1.0

        code_run = code_para.add_run(code_content)
        code_run.font.name = "Courier New"
        code_run.font.size = Pt(9)

    @staticmethod
    def generate_filename(work_number: str, student_name: str) -> str:
        safe_name = student_name.replace(" ", "_")
        return f"Отчёт_по_практической_работе_№{work_number}_{safe_name}.docx"
