from app import app, response
from app.controller import AdminsController, CategoriesController, ProductsController, ArticlesController, CommentsController, PredictionController, HistoryController, MemberController
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/')
def index():
    return 'Hello Flask App'

@app.route('/api/login', methods=['POST'])
def loginAdmin():
    return AdminsController.loginAdmin()

@app.route('/api/me', methods=['GET'])
@jwt_required()
def getMe():
    return AdminsController.getMe()

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
        return AdminsController.detailAdmin(id)
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
        return ProductsController.paginateAndFilterProductManage()
    else:
        return ProductsController.tambahProduct()

@app.route('/api/product/<id>', methods=["GET", "PUT", "DELETE"])
@jwt_required()
def productDetail(id):
    if request.method == 'GET':
        return ProductsController.detailProduct(id)
    elif request.method == "PUT":
        return ProductsController.ubahProduct(id)
    elif request.method == "DELETE":
        return ProductsController.hapusProduct(id)

@app.route('/api/product/guest', methods=['GET'])
def guestProduct():
    return ProductsController.paginateAndFilterProduct()

@app.route('/api/product/guest/<id>', methods=["GET"])
def productGuestDetail(id):
    return ProductsController.detailProduct(id)

@app.route('/api/article', methods=['GET', 'POST'])
@jwt_required()
def articles():
    if request.method == 'GET':
        return ArticlesController.paginateAndFilterArticlesManage()
    else:
        return ArticlesController.tambahArticle()

@app.route('/api/article/<id>', methods=["GET", "PUT", "DELETE"])
@jwt_required()
def detailArticle(id):
    if request.method == 'GET':
        return ArticlesController.detailArticleManage(id)
    elif request.method == "PUT":
        return ArticlesController.ubahArticle(id)
    elif request.method == "DELETE":
        return ArticlesController.hapusArticle(id)

@app.route('/api/article/guest', methods=['GET'])
def guestArticles():
    return ArticlesController.paginateAndFilterArticles()

@app.route('/api/article/guest/<id>', methods=['GET', 'POST'])
def guestDetailArticle(id):
    if request.method == 'GET':
        return ArticlesController.detailArticle(id)
    elif request.method == 'POST':
        return ArticlesController.tambahCommentUntukArticle(id)

@app.route('/api/comment', methods=['GET'])
@jwt_required()
def comments():
    return CommentsController.paginateAndFilterCommentsManage()

@app.route('/api/comment/<id>', methods=["GET", "DELETE"])
@jwt_required()
def commentDetail(id):
    if request.method == 'GET':
        return CommentsController.detailComment(id)
    else:
        return CommentsController.hapusComment(id)
    
@app.route('/api/predict/guest', methods=['POST'])
def prediction():
    return PredictionController.prediksi()

@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_all_history():
    return HistoryController.paginateAndFilterHistoryManage()

@app.route('/api/history/<id>', methods=['DELETE'])
@jwt_required()
def delete_history(id):
    return HistoryController.hapusHistory(id)

@app.route('/api/member/guest', methods=['GET'])
def memberGuest():
    return MemberController.indexMember()

@app.route('/api/member', methods=['GET', 'POST'])
@jwt_required()
def memberManage():
    if request.method == 'GET':
        return MemberController.indexMember()
    else:
        return MemberController.tambahMember()
    
@app.route('/api/member/<id>', methods=['PUT', 'DELETE'])
@jwt_required()
def memberDetail(id):
    if request.method == 'PUT':
        return MemberController.memperbaruiMember(id)
    else:
        return MemberController.hapusMember(id)
