from django import forms
from django.forms import formset_factory

from .models import QuizDraft
from .quizzes import validate_questions


class QuizForm(forms.Form):
    enabled = forms.BooleanField(label="Incluir evaluación en la próxima versión", required=False)
    title = forms.CharField(label="Título", max_length=200)
    pass_mark = forms.IntegerField(label="Nota mínima", min_value=0, max_value=100)
    max_attempts = forms.IntegerField(label="Intentos permitidos", min_value=1, max_value=10)
    wait_minutes = forms.IntegerField(label="Espera entre intentos (minutos)", min_value=0, max_value=10080)
    required = forms.BooleanField(label="Exigir aprobación para completar la lección", required=False)
    feedback = forms.ChoiceField(label="Mostrar soluciones", choices=QuizDraft._meta.get_field("feedback").choices)
    revision = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def __init__(self, *args, instance, **kwargs):
        kwargs["initial"] = {name: getattr(instance, name) for name in self.base_fields}
        super().__init__(*args, **kwargs)
        self.instance = instance

    def save(self, commit=True):
        for name in self.fields:
            setattr(self.instance, name, self.cleaned_data[name])
        if commit:
            self.instance.save()
        return self.instance


class QuestionForm(forms.Form):
    prompt = forms.CharField(label="Pregunta", max_length=2000, widget=forms.Textarea(attrs={"rows": 2}))
    multiple = forms.BooleanField(label="Permitir varias respuestas", required=False)
    options = forms.CharField(label="Opciones (una por línea)", widget=forms.Textarea(attrs={"rows": 4}), max_length=3005)
    correct = forms.CharField(label="Números de las opciones correctas", help_text="Cuenta desde 1. Para varias respuestas, escribe por ejemplo 1,3.", max_length=20)
    explanation = forms.CharField(label="Explicación", max_length=3000, required=False, widget=forms.Textarea(attrs={"rows": 2}))

    def clean(self):
        values = super().clean()
        if not all(key in values for key in ("prompt", "multiple", "options", "correct", "explanation")):
            return values
        try:
            correct = [int(value.strip()) - 1 for value in values["correct"].split(",")]
        except ValueError:
            self.add_error("correct", "Escribe números separados por comas, por ejemplo 1,3.")
            return values
        question = {"prompt": values["prompt"], "multiple": values["multiple"], "options": [option.strip() for option in values["options"].splitlines()], "correct": correct, "explanation": values["explanation"]}
        try:
            validate_questions([question])
        except forms.ValidationError as exc:
            self.add_error(None, exc)
        else:
            values["question"] = question
        return values


QuestionFormSet = formset_factory(QuestionForm, extra=1, max_num=20, validate_max=True, absolute_max=20, can_delete=True)


def question_initial(question):
    return {**question, "options": "\n".join(question["options"]), "correct": ",".join(str(index + 1) for index in question["correct"])}


class AttemptForm(forms.Form):
    revision = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def __init__(self, *args, quiz, answers, revision, **kwargs):
        super().__init__(*args, initial={"revision": revision}, **kwargs)
        for index, question in enumerate(quiz.questions):
            choices = [(str(option), label) for option, label in enumerate(question["options"])]
            field = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple, required=False) if question["multiple"] else forms.ChoiceField(choices=choices, widget=forms.RadioSelect, required=False)
            field.label = question["prompt"]
            selected = [str(option) for option in answers.get(str(index), [])]
            field.initial = selected if question["multiple"] else selected[0] if selected else ""
            self.fields[f"question_{index}"] = field

    def answers(self):
        result = {}
        for name, field in self.fields.items():
            if not name.startswith("question_"):
                continue
            value = self.cleaned_data[name]
            selections = value if isinstance(field, forms.MultipleChoiceField) else [value] if value else []
            result[name.removeprefix("question_")] = [int(option) for option in selections]
        return result
