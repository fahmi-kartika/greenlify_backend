import sys
sys.path.insert(0, r'D:\semester 7\Rakamin Academy\BE_REPO_3\greenlify_backend')
import pytest
from flask import json
from  app import app, db
from app.model.admins import Admins
from app.model.products import Products
from app import db
from flask_jwt_extended import decode_token

@pytest.mark.login_positive
def test_login_admin(test_client, setup_admin_data):
    response_remember = test_client.post(
      '/api/login',
      data=json.dumps({"email": "admin1@example.com", "password": "password123", "remember_me": True}),
      content_type='application/json',
    )
    data_remember = response_remember.get_json()
    assert response_remember.status_code == 200
    
    refresh_token_remember = data_remember["data"]["refresh_token"]
    assert data_remember['status'] == 'success'
    assert 'access_token' in data_remember['data']
    
    response_no_rember = test_client.post(
      '/api/login',
      data=json.dumps({"email": "admin1@example.com", "password": "password123", "remember_me": False}),
      content_type='application/json',
    )
    data_no_remember = response_no_rember.get_json()
    assert response_no_rember.status_code == 200
    
    refresh_token_no_remember = data_no_remember["data"]["refresh_token"]
    assert data_no_remember['status'] == 'success'
    assert 'access_token' in data_no_remember['data']
    
    decoded_remember = decode_token(refresh_token_remember)
    decoded_no_remember = decode_token(refresh_token_no_remember)
    assert decoded_remember["exp"] > decoded_no_remember["exp"]

@pytest.mark.login_negative
def test_login_admin_email_salah(test_client, setup_admin_data):
    response = test_client.post(
      '/api/login',
      data=json.dumps({"email": "salah@example.com", "password": "password123", "remember_me": True}),
      content_type='application/json',
    )
    data = response.get_json()
    assert response.status_code == 404
    assert data['status'] == 'fail'
    assert data['message'] == 'Email tidak terdaftar'
    assert not data['data']

@pytest.mark.login_negative
def test_login_admin_password_salah(test_client, setup_admin_data):
    response = test_client.post(
      '/api/login',
      data=json.dumps({"email": "admin1@example.com", "password": "salah", "remember_me": True}),
      content_type='application/json',
    )
    data = response.get_json()
    assert response.status_code == 401
    assert data['status'] == 'fail'
    assert data['message'] == 'Kombinasi password salah'
    assert not data['data']
    
@pytest.mark.login_negative
def test_login_admin_email_kosong(test_client, setup_admin_data):
    response = test_client.post(
      '/api/login',
      data=json.dumps({"email": "", "password": "password123", "remember_me": True}),
      content_type='application/json',
    )
    data = response.get_json()
    assert response.status_code == 400
    assert data['status'] == 'fail'
    assert data['message'] == 'Email dan password wajib diisi'
    assert not data['data']
    
@pytest.mark.login_negative
def test_login_admin_password_kosong(test_client, setup_admin_data):
    response = test_client.post(
      '/api/login',
      data=json.dumps({"email": "admin1@example.com", "password": "", "remember_me": True}),
      content_type='application/json',
    )
    data = response.get_json()
    assert response.status_code == 400
    assert data['status'] == 'fail'
    assert data['message'] == 'Email dan password wajib diisi'
    assert not data['data']

@pytest.mark.login_negative
def test_login_admin_remeberme_bukan_boolean(test_client, setup_admin_data):
    response = test_client.post(
      '/api/login',
      data=json.dumps({"email": "salah@example.com", "password": "password123", "remember_me": 'benar'}),
      content_type='application/json',
    )
    data = response.get_json()
    assert response.status_code == 400
    assert data['status'] == 'fail'
    assert data['message'] == 'Nilai remember_me harus berupa boolean'
    assert not data['data']
    
@pytest.mark.refreshToken_positive
def test_refresh_token(test_client, setup_admin_data):
    # login
    response_login = test_client.post(
      '/api/login',
      data=json.dumps({"email": "admin1@example.com", "password": "password123", "remember_me": True}),
      content_type='application/json',
    )
    assert response_login.status_code == 200
    data_login = response_login.get_json()
    refresh_token = data_login["data"]["refresh_token"]
    
    
    # Kirim request ke endpoint refresh
    response_refresh = test_client.post('/api/refresh', headers= {"Authorization": f"Bearer {refresh_token}"})
    
    # Verifikasi status respons
    assert response_refresh.status_code == 200

    # Verifikasi struktur data respons
    response_data = response_refresh.get_json()
    assert response_data['status'] == 'success'
    assert "access_token" in response_data['data']
    assert "refresh_token" in response_data['data']
    assert "access_token_expiry_time" in response_data['data']
    assert "refresh_token_expiry_time" in response_data['data']

    # Verifikasi token tidak kosong
    assert response_data["data"]["access_token"] is not None
    assert response_data["data"]["refresh_token"] is not None

@pytest.mark.refresh_token_negative
def test_refresh_token_invalid_token(test_client):
    # Token yang tidak valid
    invalid_token_header = {"Authorization": "Bearer invalid_token"}
    # Kirim request dengan token tidak valid
    response = test_client.post('/api/refresh', headers=invalid_token_header)
    # Verifikasi status dan pesan error
    assert response.status_code == 401 or 422
    
    response = test_client.post('/api/refresh')
    # Verifikasi status dan pesan error
    assert response.status_code == 401

@pytest.mark.get_me_positive
def test_get_me(test_client, setup_admin_data):
    # login
    response_login = test_client.post(
      '/api/login',
      data=json.dumps({"email": "admin1@example.com", "password": "password123", "remember_me": True}),
      content_type='application/json',
    )
    assert response_login.status_code == 200
    data_login = response_login.get_json()
    access_token = data_login["data"]["access_token"]
    
    response_get_me = test_client.get('/api/me', headers={"Authorization": f"Bearer {access_token}"})
    data_get_me = response_get_me.get_json()
    assert response_get_me.status_code == 200
    assert 'id' in data_get_me["data"]
    assert 'name' in data_get_me["data"]
    assert 'email' in data_get_me["data"]
    assert 'phone_number' in data_get_me["data"]
    assert 'gender' in data_get_me["data"]
    assert 'created_at' in data_get_me["data"]
    assert 'updated_at' in data_get_me["data"]

@pytest.mark.get_me_negative
def test_get_me(test_client, auth_header):
    
    response_get_me = test_client.get('/api/me', headers=auth_header)
    assert response_get_me.status_code == 404
    
    response_get_me = test_client.get('/api/me', headers={"Authorization": f"Bearer invalid_token"})
    assert response_get_me.status_code == 422

@pytest.mark.get_admin_positive
def test_index_get_admin_success(test_client, auth_header, setup_admin_data):

    admins = setup_admin_data
    response = test_client.get('/api/admin', headers=auth_header)
    data = response.get_json()

    # Asersi
    assert response.status_code == 200
    assert data['status'] == 'success'
    assert len(data['data']) == 2
    assert data['data'][0]['name'] == admins[0].name
    
# @pytest.mark.get_admin_negative
# def test_index_admin_failed(test_client):
#     response = test_client.get('/api/admin', headers={"Authorization": f"Bearer invalid token"})
#     assert response.status_code == 422
    
@pytest.mark.get_category_success
def test_get_category_success(test_client, auth_header, setup_test_categories):
    response = test_client.get('/api/category', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) == 2
    assert data['data'][0]['category_name'] is not None
    assert data['data'][1]['category_name'] is not None
    
@pytest.mark.get_category_failed
def test_get_category_failed(test_client, setup_test_categories):
    response = test_client.get('/api/category', headers={
            "Authorization": f"Bearer invalid token"
        })
    assert response.status_code == 422
    

@pytest.mark.insert_category_success
def test_get_category_success(test_client, auth_header, setup_test_categories):
    response = test_client.post('/api/category',headers=auth_header, data=json.dumps({"category_name":"categori 3"}), content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == 'Sukses Menambahkan Data Category'
    
    response = test_client.get('/api/category', headers=auth_header, content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) == 3
    assert data['data'][0]['category_name'] is not None
    assert data['data'][1]['category_name'] is not None
    assert data['data'][2]['category_name'] is not None

@pytest.mark.insert_category_failed
def test_get_category_failed(test_client, auth_header, setup_test_categories):
    # nama kategori kosong
    response = test_client.post('/api/category',headers=auth_header, data=json.dumps({"category_name":""}),content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'fail'
    assert not data['data'] 
    assert data['message'] == 'Nama kategori wajib diisi.'
    
    # nama kategori kurang dari 3 karakter
    response = test_client.post('/api/category',headers=auth_header, data=json.dumps({"category_name":"ca"}), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'fail'
    assert not data['data'] 
    assert data['message'] == 'Nama kategori harus terdiri dari minimal 3 karakter.'
    
    # nama kategori sudah ada
    response = test_client.post('/api/category',headers=auth_header, data=json.dumps({"category_name":"Category 1"}), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'fail'
    assert not data['data'] 
    assert data['message'] == 'Nama kategori sudah ada.'
    
    response = test_client.get('/api/category', headers=auth_header, content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) == 2
    
@pytest.mark.update_category_success
def test_update_category_success(test_client, auth_header, setup_test_categories):
    response = test_client.put('/api/category/1',headers=auth_header, data=json.dumps({"category_name":"categori baru"}), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    
    response = test_client.get('/api/category', headers=auth_header, content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['data'][0]['category_name'] == 'categori baru'

@pytest.mark.update_category_failed
def test_update_category_failed(test_client, auth_header, setup_test_categories):
    # kategori kosong
    response = test_client.put('/api/category/1',headers=auth_header, data=json.dumps({"category_name":""}), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'fail'
    assert not data['data'] 
    assert data['message'] == 'Nama kategori wajib diisi.'
    
    # kategori id tidak ditemukan
    response = test_client.put('/api/category/10',headers=auth_header, data=json.dumps({"category_name":"categori baru"}), content_type='application/json')
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'fail'
    assert not data['data'] 
    assert data['message'] == 'Kategori tidak ditemukan.'
    
    # kategori kurang dari 3 karakter
    response = test_client.put('/api/category/1',headers=auth_header, data=json.dumps({"category_name":"ca"}), content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'fail'
    assert not data['data'] 
    assert data['message'] == 'Nama kategori harus terdiri dari minimal 3 karakter.'
    
@pytest.mark.delete_category_success
def test_delete_category_success(test_client, auth_header, setup_test_categories):
    response = test_client.delete('/api/category/1',headers=auth_header,content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['data'] == 'Berhasil menghapus kategori!'
    
    response = test_client.get('/api/category', headers=auth_header, content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) == 1
    
@pytest.mark.delete_category_failed
def test_delete_category_failed(test_client, auth_header, setup_test_categories):
    # kategori id tidak ditemukan
    response = test_client.delete('/api/category/10',headers=auth_header, data=json.dumps({"category_name":"categori baru"}), content_type='application/json')
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'fail'
    assert not data['data'] 
    assert data['message'] == 'Kategori tidak ditemukan.'

@pytest.mark.products_success
@pytest.mark.get_product_success
def test_get_products(test_client, setup_test_products, auth_header):
    response = test_client.get('/api/product', headers=auth_header)

    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) == 2
    assert data['data'][0]['product_name'] == "Product 1"

@pytest.mark.products_success
@pytest.mark.add_product_success
def test_add_product(test_client, setup_test_categories, setup_test_admin, auth_header):
    category1, _ = setup_test_categories
    admin = setup_test_admin

    payload = {
        "created_by": admin.id,  # Pastikan ID admin sesuai dengan yang disiapkan di fixture
        "category_id": category1.id,
        "product_name": "New Product",
        "description": "Description of new product",
        "price": 1500.0,
        "contact": "new_contact@example.com",
        "img_file": "new_product.jpg"
    }

    response = test_client.post('/api/product', json=payload, headers=auth_header)

    # Debug untuk melihat respons API
    data = response.get_json()
    print(data)

    assert response.status_code == 201
    assert data['message'] == "Sukses Menambahkan Data Produk"


@pytest.mark.products_success
@pytest.mark.filter_product_success
def test_filter_products(test_client, setup_test_products, auth_header):
    response = test_client.get('/api/product/filter?category_name=Category 1&min_price=500&max_price=1500', headers=auth_header)

    data = response.get_json()
    print(data)
    assert response.status_code == 200
    assert len(data['data']) == 1
    assert data['data'][0]['product_name'] == "Product 1"

@pytest.mark.products_success
@pytest.mark.guest_get_product_success
def test_guest_get_products(test_client, setup_test_products):
    response = test_client.get('/api/product/guest')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) == 2
    assert data['data'][0]['product_name'] == "Product 1"

@pytest.mark.products_success
@pytest.mark.guest_filter_product_success
def test_guest_filter_products(test_client, setup_test_products):
    response = test_client.get('/api/product/guest/filter?keyword=Product')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) == 2

@pytest.mark.products_success
@pytest.mark.product_pagination_success
def test_product_pagination(test_client, setup_test_products):
    response = test_client.get('/api/product/guest/page?start=1&limit=1')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']['results']) == 1

@pytest.mark.products_success
@pytest.mark.get_product_detail_success
def test_get_product_detail(test_client, setup_test_products, auth_header):
    product1, _ = setup_test_products
    response = test_client.get(f'/api/product/{product1.id}', headers=auth_header)

    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['product_name'] == "Product 1"

@pytest.mark.products_success
@pytest.mark.update_product_success
def test_update_product(test_client, setup_test_products, auth_header):
    product1, _ = setup_test_products
    payload = {
        "created_by": product1.created_by,
        "category_id": product1.category_id,
        "product_name": "Updated Product",
        "description": "Updated description",
        "price": 1200.0,
        "contact": "updated_contact@example.com",
        "img_file": "updated_product.jpg"
    }

    response = test_client.put(f'/api/product/{product1.id}', json=payload, headers=auth_header)

    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['product_name'] == "Updated Product"

@pytest.mark.products_success
@pytest.mark.delete_product_success
def test_delete_product(test_client, setup_test_products, auth_header):
    product1, _ = setup_test_products
    response = test_client.delete(f'/api/product/{product1.id}', headers=auth_header)

    assert response.status_code == 200
    data = response.get_json()
    assert data['data'] == "Sukses menghapus produk!"

@pytest.mark.products_failed
@pytest.mark.test_get_products_invalid_token
def test_get_products_invalid_token(test_client):
    invalid_header = {"Authorization": "Bearer invalid_token"}
    response = test_client.get('/api/product', headers=invalid_header)
    assert response.status_code == 422
    
@pytest.mark.products_failed
@pytest.mark.test_add_product_invalid_payload
def test_add_product_invalid_payload(test_client, auth_header):
    payload = {
        "product_name": "",  # Nama produk kosong
        "description": "Invalid product",
        "price": -500.0,  # Harga negatif
        "contact": "",
        "img_file": "invalid.jpg"
    }

    response = test_client.post('/api/product', json=payload, headers=auth_header)

    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'fail'
    assert data['message'] == "Kolom created_by, category_id, product_name, dan price wajib diisi."
    
@pytest.mark.products_failed
@pytest.mark.test_filter_products_invalid_criteria
def test_filter_products_invalid_criteria(test_client, auth_header):
    # data kosong
    response = test_client.get('/api/product/filter?category_name=&min_price=&max_price=&keyword=', headers=auth_header)
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Silakan masukkan salah satu filter: category_name atau min_price & max_price, atau keyword.'
    
    # kategori name tidak valid
    response = test_client.get('/api/product/filter?category_name=Nonexistent', headers=auth_header)
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Kategori tidak ditemukan.'
    
    # harga tidak valid
    response = test_client.get('/api/product/filter?min_price=-1&max_price=-1', headers=auth_header)
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Harga tidak boleh bernilai negatif.'
    
    response = test_client.get('/api/product/filter?min_price=2&max_price=1', headers=auth_header)
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Harga minimum tidak boleh lebih besar dari harga maksimum.'
    
@pytest.mark.products_failed
@pytest.mark.test_guest_get_products_invalid_query
def test_guest_get_products_invalid_query(test_client):
    response = test_client.get('/api/product/guest?invalid_param=123')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) >= 0 
    
@pytest.mark.products_failed
@pytest.mark.test_get_product_detail_invalid_id
def test_get_product_detail_invalid_id(test_client, auth_header):
    response = test_client.get('/api/product/9999', headers=auth_header)  # ID tidak ada

    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'fail'
    assert data['message'] == "Produk tidak ditemukan"
    
@pytest.mark.products_failed
@pytest.mark.test_update_product_invalid_id
def test_update_product_invalid_id(test_client, auth_header):
    payload = {
        "product_name": "Updated Product",
        "description": "Updated description",
        "price": 1200.0,
        "contact": "updated_contact@example.com",
        "img_file": "updated_product.jpg"
    }
    response = test_client.put('/api/product/9999', json=payload, headers=auth_header)  # ID tidak ada

    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'fail'
    assert data['message'] == "Produk tidak ditemukan."
    
@pytest.mark.products_failed
@pytest.mark.test_delete_product_invalid_id
def test_delete_product_invalid_id(test_client, auth_header):
    response = test_client.delete('/api/product/9999', headers=auth_header)  # ID tidak ada

    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'fail'
    assert data['message'] == "Produk tidak ditemukan."
    
@pytest.mark.products_failed
@pytest.mark.test_product_pagination_invalid_params
def test_product_pagination_invalid_params(test_client):
    response = test_client.get('/api/product/guest/page?start=-1&limit=-5')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']['results']) == 0  # Tidak ada hasil karena parameter tidak valid
