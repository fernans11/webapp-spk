from __future__ import annotations
import json
import numpy as np
from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy import and_
from . import db
from .models import Criterion, Alternative, AlternativeValue, Pairwise, AhpResult
from .forms import CriterionForm, AlternativeForm
from .methods import AHP, ProfileMatching

bp = Blueprint("main", __name__)

def _guard_non_dummy():
    criteria = Criterion.query.count()
    alternatives = Alternative.query.count()
    if criteria == 0:
        flash("Anda belum menambahkan Kriteria beserta Sumber. Perhitungan belum dapat dijalankan.", "warning")
        return False
    if alternatives == 0:
        flash("Anda belum menambahkan Alternatif (produk sepatu) beserta Sumber. Perhitungan belum dapat dijalankan.", "warning")
        return False
    # pastikan semua alternatif punya nilai untuk semua kriteria
    crit_ids = [c.id for c in Criterion.query.order_by(Criterion.id).all()]
    for alt in Alternative.query.order_by(Alternative.id).all():
        vals = {v.criterion_id for v in AlternativeValue.query.filter_by(alternative_id=alt.id).all()}
        missing = [cid for cid in crit_ids if cid not in vals]
        if missing:
            flash(f"Alternatif '{alt.name}' belum memiliki nilai untuk semua kriteria. Lengkapi di menu Data Alternatif.", "warning")
            return False
    return True

@bp.get("/")
def index():
    last = AhpResult.query.order_by(AhpResult.created_at.desc()).first()
    return render_template("index.html", last=last)

@bp.route("/criteria", methods=["GET","POST"])
def criteria():
    form = CriterionForm()
    if form.validate_on_submit():
        c = Criterion(
            name=form.name.data.strip(),
            ctype=form.ctype.data,
            unit=form.unit.data.strip() if form.unit.data else None,
            source_title=form.source_title.data.strip(),
            source_url=form.source_url.data.strip(),
        )
        try:
            db.session.add(c)
            db.session.commit()
            flash("Kriteria berhasil ditambahkan.", "success")
            return redirect(url_for("main.criteria"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal menambah kriteria: {e}", "danger")
    items = Criterion.query.order_by(Criterion.id).all()
    return render_template("criteria.html", form=form, items=items)

@bp.post("/criteria/<int:cid>/delete")
def criteria_delete(cid: int):
    c = Criterion.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    flash("Kriteria dihapus.", "info")
    return redirect(url_for("main.criteria"))

@bp.route("/alternatives", methods=["GET","POST"])
def alternatives():
    form = AlternativeForm()
    if form.validate_on_submit():
        a = Alternative(
            name=form.name.data.strip(),
            brand=form.brand.data.strip() if form.brand.data else None,
            sport=form.sport.data.strip() if form.sport.data else None,
            source_title=form.source_title.data.strip(),
            source_url=form.source_url.data.strip(),
        )
        try:
            db.session.add(a)
            db.session.commit()
            flash("Alternatif berhasil ditambahkan.", "success")
            return redirect(url_for("main.alternatives"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal menambah alternatif: {e}", "danger")
    items = Alternative.query.order_by(Alternative.id).all()
    return render_template("alternatives.html", form=form, items=items)

@bp.post("/alternatives/<int:aid>/delete")
def alternatives_delete(aid: int):
    a = Alternative.query.get_or_404(aid)
    db.session.delete(a)
    db.session.commit()
    flash("Alternatif dihapus.", "info")
    return redirect(url_for("main.alternatives"))

@bp.route("/data", methods=["GET","POST"])
def data():
    criteria = Criterion.query.order_by(Criterion.id).all()
    alternatives = Alternative.query.order_by(Alternative.id).all()

    if request.method == "POST":
        # Simpan nilai
        try:
            for alt in alternatives:
                for crit in criteria:
                    key = f"v_{alt.id}_{crit.id}"
                    raw = request.form.get(key, "").strip()
                    if raw == "":
                        raise ValueError(f"Nilai kosong untuk {alt.name} - {crit.name}")
                    val = float(raw)

                    existing = AlternativeValue.query.filter_by(alternative_id=alt.id, criterion_id=crit.id).first()
                    if existing:
                        existing.value = val
                    else:
                        db.session.add(AlternativeValue(alternative_id=alt.id, criterion_id=crit.id, value=val))
            db.session.commit()
            flash("Data alternatif berhasil disimpan.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal menyimpan data: {e}", "danger")
        return redirect(url_for("main.data"))

    # prepare current values
    value_map = {}
    for v in AlternativeValue.query.all():
        value_map[(v.alternative_id, v.criterion_id)] = v.value

    return render_template("data.html", criteria=criteria, alternatives=alternatives, value_map=value_map)

@bp.route("/ahp", methods=["GET","POST"])
def ahp():
    criteria = Criterion.query.order_by(Criterion.id).all()
    n = len(criteria)
    if n < 2:
        flash("Tambahkan minimal 2 kriteria untuk AHP.", "warning")
        return redirect(url_for("main.criteria"))

    # build current pairwise values (upper triangle)
    current = {}
    for p in Pairwise.query.all():
        current[(p.criterion_i_id, p.criterion_j_id)] = p.value

    if request.method == "POST":
        try:
            # save all upper-triangle inputs
            for i in range(n):
                for j in range(i+1, n):
                    ci, cj = criteria[i].id, criteria[j].id
                    raw = request.form.get(f"p_{ci}_{cj}", "").strip()
                    if raw == "":
                        raise ValueError("Ada nilai perbandingan berpasangan yang kosong.")
                    val = float(raw)
                    if val <= 0:
                        raise ValueError("Nilai AHP harus > 0.")
                    existing = Pairwise.query.filter_by(criterion_i_id=ci, criterion_j_id=cj).first()
                    if existing:
                        existing.value = val
                    else:
                        db.session.add(Pairwise(criterion_i_id=ci, criterion_j_id=cj, value=val))
            db.session.commit()

            # compute matrix
            mat = np.ones((n, n), dtype=float)
            for i in range(n):
                for j in range(i+1, n):
                    ci, cj = criteria[i].id, criteria[j].id
                    v = Pairwise.query.filter_by(criterion_i_id=ci, criterion_j_id=cj).first().value
                    mat[i, j] = v
                    mat[j, i] = 1.0 / v

            weights, cr = AHP.calculate_weights(mat)
            weights_map = {criteria[idx].id: float(weights[idx]) for idx in range(n)}

            db.session.add(AhpResult(weights_json=json.dumps(weights_map), cr=float(cr)))
            db.session.commit()

            flash(f"Bobot AHP dihitung. CR = {cr:.4f}", "success")
            if cr >= 0.10:
                flash("CR >= 0.10 (kurang konsisten). Pertimbangkan revisi perbandingan berpasangan.", "warning")

            return redirect(url_for("main.ahp"))
        except Exception as e:
            db.session.rollback()
            flash(f"Gagal menghitung AHP: {e}", "danger")

    last = AhpResult.query.order_by(AhpResult.created_at.desc()).first()
    last_weights = json.loads(last.weights_json) if last else None

    return render_template("ahp.html", criteria=criteria, current=current, last=last, last_weights=last_weights)

@bp.get("/results")
def results():
    if not _guard_non_dummy():
        return redirect(url_for("main.index"))

    criteria = Criterion.query.order_by(Criterion.id).all()
    alternatives = Alternative.query.order_by(Alternative.id).all()

    last = AhpResult.query.order_by(AhpResult.created_at.desc()).first()
    if not last:
        flash("Anda belum menjalankan AHP untuk menghasilkan bobot kriteria.", "warning")
        return redirect(url_for("main.ahp"))

    weights_map = json.loads(last.weights_json)
    weights = np.array([weights_map[str(c.id)] if isinstance(next(iter(weights_map.keys())), str) else weights_map[c.id] for c in criteria], dtype=float)

    # decision matrix
    m = len(alternatives); n = len(criteria)
    decision = np.zeros((m, n), dtype=float)
    for ai, alt in enumerate(alternatives):
        for ci, crit in enumerate(criteria):
            v = AlternativeValue.query.filter_by(alternative_id=alt.id, criterion_id=crit.id).first()
            decision[ai, ci] = v.value

    # ideal profile: benefit -> max, cost -> min
    ideal = []
    for ci, crit in enumerate(criteria):
        col = decision[:, ci]
        ideal.append(float(col.max()) if crit.ctype == "benefit" else float(col.min()))
    ideal = np.array(ideal, dtype=float)

    # profile matching: use gap to ideal then convert to score
    # We'll transform: score = 1 / (1 + abs(gap))  (simple, monotonic), then weighted sum.
    gaps = decision - ideal
    scores = 1.0 / (1.0 + np.abs(gaps))
    final = scores.dot(weights)

    ranked = sorted(
        [{"name": a.name, "brand": a.brand, "sport": a.sport, "score": float(final[i]), "source_url": a.source_url} for i, a in enumerate(alternatives)],
        key=lambda x: x["score"],
        reverse=True,
    )

    return render_template("results.html", ranked=ranked, criteria=criteria, alternatives=alternatives, weights=weights, cr=last.cr)
