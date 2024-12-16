from app.model.admins import Admins
from app.model.products import Products
from app import response, db
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import *
from datetime import datetime, timedelta
import re
import os

def indexAdmin():
    try:
        admins = Admins.query.all()
        data = formatArray(admins)
        return response.success(data)
    except Exception as e:
        print(e)
        return response.serverError([], "Gagal mengambil data admin.")

def formatArray(datas):
    return [satuAdmin(data) for data in datas]

def satuAdmin(data):
    return {
        'id': data.id,
        'name': data.name,
        'email': data.email,
        'phone_number': data.phone_number,
        'gender': data.gender,
        'created_at': data.created_at,
        'updated_at': data.updated_at
    }

def detailAdmin(id):
    try:
        admin = Admins.query.filter_by(id=id).first()
        if not admin:
            return response.notFound([], 'Admin tidak ditemukan')

        products = Products.query.filter_by(created_by=id).all()
        data = satuDetailAdmin(admin, products)

        return response.success(data)
    except Exception as e:
        print(e)
        return response.serverError([], "Gagal mengambil detail admin.")

def satuDetailAdmin(admin, products):
    return {
        'id': admin.id,
        'name': admin.name,
        'email': admin.email,
        'phone_number': admin.phone_number,
        'gender': admin.gender,
        'created_at': admin.created_at,
        'updated_at': admin.updated_at,
        'products': [satuProduct(product) for product in products]
    }

def satuProduct(product):
    return {
        'id': product.id,
        'created_by': product.admin.name,
        'category_name': product.category.category_name,
        'product_name': product.product_name,
        'description': product.description,
        'price': str(product.price),
        'contact': product.contact,
        'img_file': product.img_file,
        'created_at': product.created_at,
        'updated_at': product.updated_at
    }

def tambahAdmin():
    try:
        name = request.form.get('name') or request.json.get('name')
        email = request.form.get('email') or request.json.get('email')
        password = request.form.get('password') or request.json.get('password')
        phone_number = request.form.get('phone_number') or request.json.get('phone_number')
        gender = request.form.get('gender') or request.json.get('gender')

        if not (name):
            return response.badRequest([], "Kolom name wajib diisi.")
        
        if not (email):
            return response.badRequest([], "Kolom email wajib diisi.")
        
        if not (password):
            return response.badRequest([], "Kolom password wajib diisi.")
        
        if not (phone_number):
            return response.badRequest([], "Kolom phone_number wajib diisi.")
        
        if not (gender):
            return response.badRequest([], "Kolom gender wajib diisi.")

        if len(password) < 8:
            return response.badRequest([], "Kata sandi harus terdiri dari minimal 8 karakter.")

        if gender not in ["Laki-Laki", "Perempuan"]:
            return response.badRequest([], "Jenis kelamin tidak valid. Gunakan 'Laki-Laki' atau 'Perempuan'.")

        if Admins.query.filter_by(email=email).first():
            return response.badRequest([], "Email sudah terdaftar.")

        if Admins.query.filter_by(phone_number=phone_number).first():
            return response.badRequest([], "Nomor telepon sudah terdaftar.")
        
        if not re.match("^[a-zA-Z\s]+$", name) or len(name) < 3 or len(name) > 50:
            return response.badRequest([], "Nama hanya boleh huruf, panjang 3-50 karakter.")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return response.badRequest([], "Format email tidak valid.")

        if not re.match("^\d{10,15}$", phone_number):
            return response.badRequest([], "Nomor telepon hanya boleh angka, panjang 10-15 digit.")

        if not re.match(r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
            return response.badRequest([], "Password harus memiliki minimal 8 karakter, 1 huruf besar, 1 angka, dan 1 simbol.")


        admin = Admins(
            name=name,
            email=email,
            phone_number=phone_number,
            gender=gender
        )
        admin.setPassword(password)
        db.session.add(admin)
        db.session.commit()

        return response.created([], 'Sukses Menambahkan Data Admin')
    except Exception as e:
        db.session.rollback()
        print(e)
        return response.serverError([], "Gagal menyimpan data admin.")

def ubahAdmin(id):
    try:
        admin = Admins.query.filter_by(id=id).first()
        if not admin:
            return response.notFound([], "Admin tidak ditemukan.")

        name = request.form.get('name') or request.json.get('name')
        email = request.form.get('email') or request.json.get('email')
        password = request.form.get('password') or request.json.get('password')
        phone_number = request.form.get('phone_number') or request.json.get('phone_number')
        gender = request.form.get('gender') or request.json.get('gender')

        if not (name):
            return response.badRequest([], "Kolom name wajib diisi.")
        
        if not (email):
            return response.badRequest([], "Kolom email wajib diisi.")
        
        if not (password):
            return response.badRequest([], "Kolom password wajib diisi.")
        
        if not (phone_number):
            return response.badRequest([], "Kolom phone_number wajib diisi.")
        
        if not (gender):
            return response.badRequest([], "Kolom gender wajib diisi.")

        if gender not in ["Laki-Laki", "Perempuan"]:
            return response.badRequest([], "Jenis kelamin tidak valid. Gunakan 'Laki-Laki' atau 'Perempuan'.")
        
        if name and (not re.match("^[a-zA-Z\s]+$", name) or len(name) < 3 or len(name) > 50):
            return response.badRequest([], "Nama hanya boleh huruf, panjang 3-50 karakter.")

        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return response.badRequest([], "Format email tidak valid.")

        if phone_number and not re.match("^\d{10,15}$", phone_number):
            return response.badRequest([], "Nomor telepon hanya boleh angka, panjang 10-15 digit.")

        if password and not re.match(r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
            return response.badRequest([], "Password harus memiliki minimal 8 karakter, 1 huruf besar, 1 angka, dan 1 simbol.")

        admin.name = name
        admin.email = email
        admin.password = generate_password_hash(password)
        admin.phone_number = phone_number
        admin.gender = gender

        db.session.commit()

        return response.success(satuAdmin(admin))
    except Exception as e:
        db.session.rollback()
        print(e)
        return response.serverError([], "Gagal mengubah data admin.")

def hapusAdmin(id):
    try:
        admin = Admins.query.filter_by(id=id).first()   
        if not admin:
            return response.notFound([], "Data admin tidak ditemukan.")

        db.session.delete(admin)
        db.session.commit()

        return response.success('Sukses menghapus admin!')
    except Exception as e:
        db.session.rollback()
        print(e)
        return response.serverError([], "Gagal menghapus data admin.")
    
def loginAdmin():
    try:
        email = request.form.get('email') or request.json.get('email')
        password = request.form.get('password') or request.json.get('password')
        remember_me = request.form.get('remember_me') or request.json.get('remember_me')

        if remember_me is None:
            remember_me = False

        if not isinstance(remember_me, bool):
            return response.badRequest([], 'Nilai remember_me harus berupa boolean')

        admin = Admins.query.filter_by(email=email).first()

        if not email or not password:
            return response.badRequest([],'Email dan password wajib diisi')

        if not admin:
            return response.notFound([],'Email tidak terdaftar')
        
        if not admin.checkPassword(password):
            return response.unauthorized([], 'Kombinasi password salah')
  
        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return response.badRequest([], "Format email tidak valid.")

        if password and len(password) > 50:  
            return response.badRequest([], "Password terlalu panjang, maksimal 50 karakter.")
        
        data = satuAdmin(admin)

        expires = timedelta(days=3) if remember_me else timedelta(hours=12)
        additional_claims = {'remember_me': remember_me}

        access_token = create_access_token(identity=admin.email, fresh=True, expires_delta=expires, additional_claims=additional_claims)

        access_token_expiry_time = datetime.utcnow() + expires

        return response.success({
            "data" : data,
            "access_token" : access_token,
            "access_token_expiry_time": access_token_expiry_time.isoformat(),
        })
    except Exception as e:
        print(e)
        return response.serverError([], "Gagal login")

def getMe():
        try:
            current_user_email = get_jwt_identity()

            admin = Admins.query.filter_by(email=current_user_email).first()

            if not admin:
                return response.notFound([],"Admin tidak ditemukan")

            data = satuAdmin(admin)

            return response.success(data)
        
        except Exception as e:
            print(e)
            return response.serverError([],"Gagal mengambil data admin")