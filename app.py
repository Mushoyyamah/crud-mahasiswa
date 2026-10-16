from datetime import date
import sqlite3

from flask import (
    Flask, flash, redirect, render_template,
    request, url_for
)

from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = "ganti-dengan-secret-key-anda"


def tahun_sekarang():
    return date.today().year


def validasi(form, nim_wajib=True):
    data = {
        "nim": form.get("nim", "").strip(),
        "nama": form.get("nama", "").strip(),
        "program_studi": form.get("program_studi", "").strip(),
        "angkatan": form.get("angkatan", "").strip(),
        "ipk": form.get("ipk", "").strip(),
    }
    errors = []

    if nim_wajib:
        try:
            data["nim"] = int(data["nim"])
            if data["nim"] <= 0:
                errors.append("NIM harus bilangan bulat positif.")
        except ValueError:
            errors.append("NIM wajib diisi dengan bilangan bulat.")

    if not data["nama"]:
        errors.append("Nama wajib diisi.")

    if not data["program_studi"]:
        errors.append("Program studi wajib diisi.")

    try:
        data["angkatan"] = int(data["angkatan"])
        if not 1900 <= data["angkatan"] <= tahun_sekarang():
            errors.append("Angkatan harus berupa tahun yang valid.")
    except ValueError:
        errors.append("Angkatan wajib diisi dengan bilangan bulat.")

    try:
        data["ipk"] = float(data["ipk"])
        if not 0 <= data["ipk"] <= 4:
            errors.append("IPK harus berada pada rentang 0,00–4,00.")
    except ValueError:
        errors.append("IPK wajib diisi dengan angka.")

    return data, errors


@app.route("/")
def index():
    with get_db_connection() as db:
        rows = db.execute(
            "SELECT * FROM mahasiswa ORDER BY nim"
        ).fetchall()

    tahun = tahun_sekarang()
    mahasiswa = [
        {
            **dict(row),
            "lama_studi": tahun - row["angkatan"]
        }
        for row in rows
    ]
    return render_template(
        "index.html",
        mahasiswa=mahasiswa,
        tahun_sekarang=tahun
    )


@app.route("/mahasiswa/tambah", methods=["GET", "POST"])
def tambah():
    if request.method == "POST":
        data, errors = validasi(request.form)

        if not errors:
            try:
                with get_db_connection() as db:
                    db.execute("""
                        INSERT INTO mahasiswa
                        (nim, nama, program_studi, angkatan, ipk)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        data["nim"], data["nama"],
                        data["program_studi"],
                        data["angkatan"], data["ipk"]
                    ))
                flash("Mahasiswa berhasil ditambahkan.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                errors.append("NIM sudah terdaftar.")

        for error in errors:
            flash(error, "error")

        return render_template(
            "form.html", mode="tambah",
            mahasiswa=request.form,
            tahun_sekarang=tahun_sekarang()
        )

    return render_template(
        "form.html", mode="tambah", mahasiswa={},
        tahun_sekarang=tahun_sekarang()
    )


@app.route("/mahasiswa/<int:nim>")
def detail(nim):
    with get_db_connection() as db:
        row = db.execute(
            "SELECT * FROM mahasiswa WHERE nim = ?", (nim,)
        ).fetchone()

    if row is None:
        flash("Data mahasiswa tidak ditemukan.", "error")
        return redirect(url_for("index"))

    mahasiswa = dict(row)
    mahasiswa["lama_studi"] = (
        tahun_sekarang() - mahasiswa["angkatan"]
    )
    return render_template("detail.html", mahasiswa=mahasiswa)


@app.route("/mahasiswa/<int:nim>/edit", methods=["GET", "POST"])
def edit(nim):
    with get_db_connection() as db:
        row = db.execute(
            "SELECT * FROM mahasiswa WHERE nim = ?", (nim,)
        ).fetchone()

    if row is None:
        flash("Data mahasiswa tidak ditemukan.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        data, errors = validasi(request.form, nim_wajib=False)

        if not errors:
            try:
                with get_db_connection() as db:
                    db.execute("""
                        UPDATE mahasiswa
                        SET nama = ?, program_studi = ?,
                            angkatan = ?, ipk = ?
                        WHERE nim = ?
                    """, (
                        data["nama"], data["program_studi"],
                        data["angkatan"], data["ipk"], nim
                    ))
                flash("Data mahasiswa berhasil diperbarui.", "success")
                return redirect(url_for("detail", nim=nim))
            except sqlite3.IntegrityError:
                errors.append("Data tidak memenuhi ketentuan database.")

        for error in errors:
            flash(error, "error")

        data["nim"] = nim
        return render_template(
            "form.html", mode="edit", mahasiswa=data,
            tahun_sekarang=tahun_sekarang()
        )

    return render_template(
        "form.html", mode="edit", mahasiswa=dict(row),
        tahun_sekarang=tahun_sekarang()
    )


@app.route("/mahasiswa/<int:nim>/hapus", methods=["POST"])
def hapus(nim):
    with get_db_connection() as db:
        cursor = db.execute(
            "DELETE FROM mahasiswa WHERE nim = ?", (nim,)
        )
        berhasil = cursor.rowcount > 0

    if berhasil:
        flash("Data mahasiswa berhasil dihapus.", "success")
    else:
        flash("Data mahasiswa tidak ditemukan.", "error")

    return redirect(url_for("index"))


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)