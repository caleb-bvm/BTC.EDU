"""Validation shared by editable assessments and their publication snapshots."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext


def validate_questions(questions):
    if not isinstance(questions, list) or not 1 <= len(questions) <= 20:
        raise ValidationError(gettext("Incluye entre 1 y 20 preguntas."))
    for question in questions:
        if not isinstance(question, dict) or set(question) != {"prompt", "multiple", "options", "correct", "explanation"}:
            raise ValidationError(gettext("La pregunta no tiene un formato válido."))
        if not isinstance(question["prompt"], str) or not question["prompt"].strip() or len(question["prompt"]) > 2000:
            raise ValidationError(gettext("Cada pregunta necesita un enunciado de hasta 2000 caracteres."))
        if type(question["multiple"]) is not bool:
            raise ValidationError(gettext("Indica si la pregunta admite varias respuestas."))
        options = question["options"]
        if not isinstance(options, list) or not 2 <= len(options) <= 6 or any(not isinstance(option, str) or not option.strip() or len(option) > 500 for option in options):
            raise ValidationError(gettext("Incluye de 2 a 6 opciones de hasta 500 caracteres."))
        if len(set(options)) != len(options):
            raise ValidationError(gettext("Las opciones deben ser diferentes."))
        correct = question["correct"]
        if not isinstance(correct, list) or not correct or any(type(index) is not int or not 0 <= index < len(options) for index in correct) or len(set(correct)) != len(correct):
            raise ValidationError(gettext("Selecciona respuestas correctas que existan, sin repetirlas."))
        if not question["multiple"] and len(correct) != 1:
            raise ValidationError(gettext("Una pregunta de selección única tiene una respuesta correcta."))
        if not isinstance(question["explanation"], str) or len(question["explanation"]) > 3000:
            raise ValidationError(gettext("La explicación admite hasta 3000 caracteres."))
