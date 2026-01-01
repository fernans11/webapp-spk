from datetime import datetime
from . import db

class Criterion(db.Model):
    __tablename__ = "criteria"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    ctype = db.Column(db.String(10), nullable=False)  # benefit | cost
    unit = db.Column(db.String(50), nullable=True)

    source_title = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(500), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Alternative(db.Model):
    __tablename__ = "alternatives"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, unique=True)
    brand = db.Column(db.String(80), nullable=True)
    sport = db.Column(db.String(80), nullable=True)

    source_title = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.String(500), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AlternativeValue(db.Model):
    __tablename__ = "alternative_values"
    id = db.Column(db.Integer, primary_key=True)
    alternative_id = db.Column(db.Integer, db.ForeignKey("alternatives.id", ondelete="CASCADE"), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    value = db.Column(db.Float, nullable=False)

    alternative = db.relationship("Alternative", backref=db.backref("values", cascade="all, delete-orphan"))
    criterion = db.relationship("Criterion")

    __table_args__ = (db.UniqueConstraint("alternative_id", "criterion_id", name="uq_alt_crit"),)

class Pairwise(db.Model):
    __tablename__ = "pairwise"
    id = db.Column(db.Integer, primary_key=True)
    criterion_i_id = db.Column(db.Integer, db.ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    criterion_j_id = db.Column(db.Integer, db.ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    value = db.Column(db.Float, nullable=False)  # i vs j

    criterion_i = db.relationship("Criterion", foreign_keys=[criterion_i_id])
    criterion_j = db.relationship("Criterion", foreign_keys=[criterion_j_id])

    __table_args__ = (db.UniqueConstraint("criterion_i_id", "criterion_j_id", name="uq_pairwise"),)

class AhpResult(db.Model):
    __tablename__ = "ahp_result"
    id = db.Column(db.Integer, primary_key=True)
    weights_json = db.Column(db.Text, nullable=False)  # {criterion_id: weight}
    cr = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
