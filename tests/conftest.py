import sys
sys.path.insert(0, r'D:\semester 7\Rakamin Academy\BE_REPO_3\greenlify_backend')
import pytest
from app import app, db
from flask_jwt_extended import create_access_token
from config import Config
from app.model.admins import Admins
from app.model.categories import Categories
from app.model.products import Products

@pytest.fixture
def setup_admin_data():
    # Tambahkan data admin ke database
    admin1 = Admins(
        name="Admin1",
        email="admin1@example.com",
        phone_number="1234567890",
        gender="Laki-Laki"
    )
    admin1.setPassword("password123")

    admin2 = Admins(
        name="Admin2",
        email="admin2@example.com",
        phone_number="0987654321",
        gender="Perempuan"
    )
    admin2.setPassword("password456")

    db.session.add(admin1)
    db.session.add(admin2)
    db.session.commit()  # Simpan ke database

    # Fixture memberikan data admin untuk test
    yield [admin1, admin2]

    # Bersihkan database (teardown)
    db.session.delete(admin1)
    db.session.delete(admin2)
    db.session.commit()


@pytest.fixture()
def test_client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_ECHO'] = True  # Menampilkan query SQL

    with app.app_context():
        db.create_all()  # Buat semua tabel
        client = app.test_client()
        yield client
        db.session.remove()
        db.drop_all()  # Bersihkan database setelah pengujian

@pytest.fixture
def auth_header():
    with app.app_context():
        # Buat token dengan identitas pengguna (email contoh)
        access_token = create_access_token(identity="admin1@example.com")
        return {
            "Authorization": f"Bearer {access_token}"
        }

@pytest.fixture
def setup_test_categories():
    # Setup data kategori
    category1 = Categories(category_name="Category 1")
    category2 = Categories(category_name="Category 2")
    db.session.add(category1)
    db.session.add(category2)
    db.session.commit()
    # Yield untuk test
    yield [category1, category2]
    db.session.query(Categories).delete()
    db.session.commit()
    
@pytest.fixture
def setup_test_products(setup_test_categories, setup_admin_data):
    category1, category2 = setup_test_categories
    admin1, _ = setup_admin_data

    product1 = Products(
        created_by=admin1.id,
        category_id=category1.id,
        product_name="Product 1",
        description="Description of Product 1",
        price=1000.0,
        contact="contact1@example.com",
        img_file="product1.jpg"
    )
    product2 = Products(
        created_by=admin1.id,
        category_id=category2.id,
        product_name="Product 2",
        description="Description of Product 2",
        price=2000.0,
        contact="contact2@example.com",
        img_file="product2.jpg"
    )

    db.session.add(product1)
    db.session.add(product2)
    db.session.commit()

    yield [product1, product2]

    db.session.query(Products).delete()
    db.session.commit()

@pytest.fixture
def setup_test_admin():
    from app.model.admins import Admins

    admin = Admins(name="Admin Test", email="admin@example.com", phone_number="1234567890", gender="Laki-Laki")
    admin.setPassword("password123")

    db.session.add(admin)
    db.session.commit()

    yield admin  # Kembalikan objek admin untuk digunakan di test

    # Bersihkan data setelah test selesai
    db.session.query(Admins).delete()
    db.session.commit()
