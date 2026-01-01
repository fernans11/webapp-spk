import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, URL, NumberRange, ValidationError, Optional

URL_REJECT = re.compile(r"(localhost|127\.0\.0\.1)", re.IGNORECASE)

def reject_local_url(form, field):
    if field.data and URL_REJECT.search(field.data):
        raise ValidationError("URL sumber tidak boleh localhost/127.0.0.1. Gunakan URL publik yang valid.")

class CriterionForm(FlaskForm):
    name = StringField("Nama Kriteria", validators=[DataRequired(), Length(min=2, max=120)])
    ctype = SelectField("Tipe Kriteria", choices=[("benefit","Benefit (semakin besar semakin baik)"),("cost","Cost (semakin kecil semakin baik)")], validators=[DataRequired()])
    unit = StringField("Satuan (opsional)", validators=[Optional(), Length(max=50)])

    source_title = StringField("Judul Sumber", validators=[DataRequired(), Length(min=5, max=200)])
    source_url = StringField("URL Sumber", validators=[DataRequired(), URL(), reject_local_url, Length(max=500)])

    submit = SubmitField("Simpan")

class AlternativeForm(FlaskForm):
    name = StringField("Nama Alternatif (Nama Sepatu)", validators=[DataRequired(), Length(min=3, max=160)])
    brand = StringField("Brand (opsional)", validators=[Optional(), Length(max=80)])
    sport = StringField("Jenis Olahraga (opsional)", validators=[Optional(), Length(max=80)])

    source_title = StringField("Judul Sumber", validators=[DataRequired(), Length(min=5, max=200)])
    source_url = StringField("URL Sumber", validators=[DataRequired(), URL(), reject_local_url, Length(max=500)])

    submit = SubmitField("Simpan")

class PairwiseCellForm(FlaskForm):
    value = FloatField("Nilai", validators=[DataRequired(), NumberRange(min=1/9, max=9)])
