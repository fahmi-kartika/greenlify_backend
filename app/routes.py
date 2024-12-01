from app import app, response
from app.controller import AdminsController, CategoriesController, ProductsController
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controller.ProductsController import Products, format_array

@app.route('/')
def index():
    return 'Hello Flask App'

@app.route('/api/login', methods=['POST'])
def loginAdmin():
    return AdminsController.loginAdmin()

@app.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    return AdminsController.refreshToken()

@app.route('/api/me', methods=['GET'])
@jwt_required()
def getMe():
    return AdminsController.get_me()

@app.route('/api/admin', methods=['GET', 'POST'])
@jwt_required()
def admins():
    if request.method == 'GET':
        return AdminsController.indexAdmin()
    else:
        return AdminsController.tambahAdmin()
    
@app.route('/api/admin/<id>', methods=["GET", "PUT", "DELETE"])
@jwt_required()
def adminDetail(id):
    if request.method == 'GET':
        return AdminsController.detail_admin(id)
    elif request.method == "PUT":
        return AdminsController.ubahAdmin(id)
    elif request.method == "DELETE":
        return AdminsController.hapusAdmin(id)

@app.route('/api/category', methods=['GET', 'POST'])
@jwt_required()
def categories():
    if request.method == 'GET':
        return CategoriesController.indexCategory()
    else:
        return CategoriesController.tambahCategory()
    
# @app.route('/api/category/filter', methods=['GET'])
# @jwt_required()
# def filterCategory():
#     return CategoriesController.filterCategory()

@app.route('/api/category/<id>', methods=["PUT", "DELETE"])
@jwt_required()
def categoryDetail(id):
    if request.method == "PUT":
        return CategoriesController.ubahCategory(id)
    else:
        return CategoriesController.hapusCategory(id)

@app.route('/api/product', methods=['GET', 'POST'])
@jwt_required()
def products():
    if request.method == 'GET':
        return ProductsController.indexProduct()
    else:
        return ProductsController.tambahProduct()
    
@app.route('/api/product/filter', methods=['GET'])
@jwt_required()
def filterProductManage():
    return ProductsController.filterProductsManage()
        
@app.route('/api/product/guest', methods=['GET'])
def guestProduct():
    return ProductsController.indexGuest()

@app.route('/api/product/guest/filter', methods=['GET'])
def filterProduct():
    return ProductsController.filterProducts()

@app.route('/api/product/guest/page', methods=['GET'])
def pagination():
    return ProductsController.paginate()

@app.route('/api/product/<id>', methods=["GET", "PUT", "DELETE"])
@jwt_required()
def productDetail(id):
    if request.method == 'GET':
        return ProductsController.detail_product(id)
    elif request.method == "PUT":
        return ProductsController.ubahProduct(id)
    elif request.method == "DELETE":
        return ProductsController.hapusProduct(id)

