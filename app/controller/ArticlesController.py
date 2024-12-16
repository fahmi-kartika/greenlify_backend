from flask import request
from app.model.articles import Articles
from app.model.admins import Admins
from app.model.comments import Comments
from app import response, db, app, uploadconfig
import re, os, uuid
from werkzeug.utils import secure_filename

def indexArticle():
    try:
        articles = Articles.query.all()
        data = formatArray(articles)
        return response.success(data)
    except Exception as e:
        print(e)
        return response.serverError([], "Gagal mengambil data artikel.")

def formatArray(datas):
    return [satuArticle(data) for data in datas]

def satuArticle(data):
    return {
        'id': data.id,
        'title': data.title,
        'content': data.content,
        'views': data.views,
        'created_by': data.admin.name,
        'img_file': data.img_file,
        'created_at': data.created_at,
        'updated_at': data.updated_at
    }

def satuComment(comment):
    return {
        'id_comment': comment.id,
        'username': comment.username,
        'email': comment.email,
        'comment': comment.comment,
        'status': comment.status.value,
        'is_approved': comment.is_approved,
        'created_at': comment.created_at
    }

def detailArticle(id):
    try:
        article = Articles.query.filter_by(id=id).first()
        if not article:
            return response.notFound([], 'Artikel tidak ditemukan.')

        article.views += 1
        db.session.commit()

        start = request.args.get('start', default=1, type=int)
        limit = request.args.get('limit', default=4, type=int)

        query = Comments.query.filter_by(id_article=id).order_by(Comments.created_at.desc())
        total_data = query.count()

        if start < 1 or limit < 1:
            return response.badRequest([], "Parameter 'start' dan 'limit' harus lebih besar dari 0.")

        comments = query.offset(start - 1).limit(limit).all()

        pagination_comment = {
            'success': True,
            'start_index': start,
            'per_page': limit,
            'total_data': total_data,
            'results': [{
                'id': comment.id,
                'username': comment.username,
                'email': comment.email,
                'comment': comment.comment,
                'created_at': comment.created_at
            } for comment in comments]
        }

        base_url = f"{os.getenv('BASE_URL')}api/article/guest/{id}"

        if start > 1:
            previous_start = max(1, start - limit)
            pagination_comment['previous'] = f"{base_url}?start={previous_start}&limit={limit}"
        else:
            pagination_comment['previous'] = None

        if start + limit <= total_data:
            next_start = start + limit
            pagination_comment['next'] = f"{base_url}?start={next_start}&limit={limit}"
        else:
            pagination_comment['next'] = None

        return response.success({
            'article': {
                'id': article.id,
                'title': article.title,
                'img_file': article.img_file,
                'content': article.content,
                'views': article.views,
                'created_by': article.admin.name,
                'created_at': article.created_at,
                'updated_at': article.updated_at
            },
            'pagination_comment': pagination_comment
        })
    except Exception as e:
        print(e)
        return response.serverError([], "Gagal mengambil detail artikel dengan komentar.")

def detailArticleManage(id):
    try:
        article = Articles.query.filter_by(id=id).first()
        if not article:
            return response.notFound([], 'Artikel tidak ditemukan.')

        return response.success(satuArticle(article))
    except Exception as e:
        print(e)
        return response.serverError([], "Gagal mengambil detail artikel.")

def tambahCommentUntukArticle(id):
    try:
        username = request.form.get('username') or request.json.get('username')
        email = request.form.get('email') or request.json.get('email')
        comment = request.form.get('comment') or request.json.get('comment')

        if not username:
            return response.badRequest([], "Kolom username wajib diisi.")
        if len(username) < 3 or len(username) > 100:
            return response.badRequest([], "Username harus memiliki panjang antara 3 hingga 100 karakter.")

        if not email:
            return response.badRequest([], "Kolom email wajib diisi.")
        
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return response.badRequest([], "Format email tidak valid.")

        if not comment:
            return response.badRequest([], "Kolom comment wajib diisi.")
        if len(comment) < 3:
            return response.badRequest([], "Comment harus memiliki panjang minimal 3 karakter.")

        article = Articles.query.filter_by(id=id).first()
        if not article:
            return response.notFound([], "Artikel tidak ditemukan.")

        new_comment = Comments(
            id_article=id,
            username=username,
            email=email,
            comment=comment,
        )

        db.session.add(new_comment)
        db.session.commit()
        return response.created([],"Sukses menambahkan komentar")

    except Exception as e:
        db.session.rollback()
        print(e)
        return response.serverError([], "Gagal menambahkan komentar.")

def tambahArticle():
    try:
        created_by = request.form.get('created_by') 
        title = request.form.get('title') 
        content = request.form.get('content') 

        if not (created_by):
            return response.badRequest([], "Kolom created_by wajib diisi.")
        
        if not (title):
            return response.badRequest([], "Kolom title wajib diisi.")
        
        if not (content):
            return response.badRequest([], "Kolom content wajib diisi.")
        
        
        if not re.match(r'^[a-zA-Z0-9 ]*$', title):
            return response.badRequest([], "Judul artikel tidak boleh mengandung karakter khusus.")

        if len(title) < 3 or len(title) > 255:
            return response.badRequest([], "Judul artikel harus antara 3 hingga 255 karakter.")

        if 'img_file' not in request.files:
            return response.badRequest([], 'File tidak tersedia')

        file = request.files['img_file']

        if file.filename == '':
            return response.badRequest([], 'File tidak tersedia')

        if file and uploadconfig.allowed_file(file.filename):
            uid = uuid.uuid4()
            filename = secure_filename(file.filename)
            renamefile = f"GreenLify-Article-{uid}-{filename}"

            save_path = os.path.join(app.config['ARTICLE_FOLDER'], renamefile)        
            file.save(save_path)
        
            file_path = os.path.join(app.config['ARTICLE_URL_PATH'], renamefile).replace('\\', '/')
            img_url = f"{os.getenv('BASE_URL')}{file_path}"

        article = Articles(
            created_by=created_by,
            title=title,
            content=content,
            img_file=img_url
        )

        db.session.add(article)
        db.session.commit()

        return response.created([], 'Sukses menambahkan artikel.')

    except Exception as e:
        db.session.rollback()
        print(e)
        return response.serverError([], f"Gagal menambahkan artikel: {str(e)}")

def ubahArticle(id):
    try:
        article = Articles.query.filter_by(id=id).first()
        if not article:
            return response.notFound([], "Artikel tidak ditemukan.")

        created_by = request.form.get('created_by')
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not (created_by):
            return response.badRequest([], "Kolom created_by wajib diisi.")
        
        if not (title):
            return response.badRequest([], "Kolom title wajib diisi.")
        
        if not (content):
            return response.badRequest([], "Kolom content wajib diisi.")
        
        if not re.match(r'^[a-zA-Z0-9 ]*$', title):
            return response.badRequest([], "Judul artikel tidak boleh mengandung karakter khusus.")

        if len(title) < 3 or len(title) > 255:
            return response.badRequest([], "Judul artikel harus antara 3 hingga 255 karakter.")
        
        if content and (len(content) < 10 or len(content) > 10000):
            return response.badRequest([], "Content harus memiliki panjang antara 10 hingga 10000 karakter.")

        if 'img_file' in request.files:
            file = request.files['img_file']
            if file.filename != '' and uploadconfig.allowed_file(file.filename):
                if article.img_file:
                    old_img_path = os.path.join(app.config['ARTICLE_FOLDER'], article.img_file.split('/')[-1])
                    if os.path.exists(old_img_path):
                        os.remove(old_img_path)

                uid = uuid.uuid4()
                filename = secure_filename(file.filename)
                img_file = f"GreenLify-Article-{uid}-{filename}"
                save_path = os.path.join(app.config['ARTICLE_FOLDER'], img_file)
                file.save(save_path)

                file_path = os.path.join(app.config['ARTICLE_URL_PATH'], img_file).replace('\\', '/')
                img_url = f"{os.getenv('BASE_URL')}{file_path}"
                article.img_file = img_url


        article.created_by = created_by
        article.title = title
        article.content = content
        db.session.commit()

        return response.success(satuArticle(article))

    except Exception as e:
        db.session.rollback()
        print(e)
        return response.serverError([], "Gagal mengubah artikel.")

def hapusArticle(id):
    try:
        article = Articles.query.filter_by(id=id).first()
        if not article:
            return response.notFound([], "Artikel tidak ditemukan.")

        if article.img_file:
            img_filename = article.img_file.split('/')[-1]
            img_path = os.path.join(app.config['ARTICLE_FOLDER'], img_filename)
            if os.path.exists(img_path):
                os.remove(img_path)

        db.session.delete(article)
        db.session.commit()
        return response.success('Sukses menghapus artikel!')

    except Exception as e:
        db.session.rollback()
        print(e)
        return response.serverError([], "Gagal menghapus artikel.")

def paginateAndFilterArticles():
    try:
        start = request.args.get('start', default=1, type=int)
        limit = request.args.get('limit', default=4, type=int)
        keyword = request.args.get('keyword', type=str)

        query = Articles.query

        if keyword:
            keyword = f"%{keyword}%"
            query = query.filter(
                Articles.title.ilike(keyword)
            )

        latest_article = Articles.query.order_by(Articles.created_at.desc()).first()

        query = query.filter(Articles.id != latest_article.id) if latest_article else query

        total_data = query.count()

        if start < 1 or limit < 1:
            return response.badRequest([], "Parameter 'start' dan 'limit' harus lebih besar dari 0.")

        articles = query.order_by(Articles.created_at.desc()).offset(start - 1).limit(limit).all()

        if not articles:
            return response.notFound([], "Tidak ada artikel yang ditemukan.")

        pagination_data = {
            'success': True,
            'start_index': start,
            'per_page': limit,
            'total_data': total_data,
            'results': formatArray(articles),
        }   

        base_url = f"{os.getenv('BASE_URL')}api/article/guest"
        
        filter_query = f"keyword={keyword}" if keyword else ""

        if start > 1:
            previous_start = max(1, start - limit)
            previous_query = f"start={previous_start}&limit={limit}"
            pagination_data['previous'] = f"{base_url}?{previous_query}&{filter_query}" if filter_query else f"{base_url}?{previous_query}"
        else:
            pagination_data['previous'] = None

        if start + limit <= total_data:
            next_start = start + limit
            next_query = f"start={next_start}&limit={limit}"
            pagination_data['next'] = f"{base_url}?{next_query}&{filter_query}" if filter_query else f"{base_url}?{next_query}"
        else:
            pagination_data['next'] = None

        final_response = {
            'latest_article': formatArray([latest_article]) if latest_article else None,
            'pagination': pagination_data
        }

        return response.success(final_response)

    except Exception as e:
        print(e)
        return response.serverError([], "Gagal mengambil data artikel.")

def paginateAndFilterArticlesManage():
    try:
        start = request.args.get('start', default=1, type=int)
        limit = request.args.get('limit', default=4, type=int)
        keyword = request.args.get('keyword', type=str)

        query = Articles.query.order_by(Articles.created_at.desc())

        if keyword:
            keyword = f"%{keyword}%"
            query = query.filter(
                Articles.title.ilike(keyword)
            )

        total_data = query.count()

        if start < 1 or limit < 1:
            return response.badRequest([], "Parameter 'start' dan 'limit' harus lebih besar dari 0.")

        articles = query.offset(start - 1).limit(limit).all()

        if not articles:
            return response.notFound([], "Tidak ada artikel yang ditemukan.")

        pagination_data = {
            'success': True,
            'start_index': start,
            'per_page': limit,
            'total_data': total_data,
            'results': []
        }

        for article in articles:
            total_comment = Comments.query.count()
            article_data = satuArticle(article)
            article_data['total_comment'] = total_comment
            pagination_data['results'].append(article_data)

        base_url =  f"{os.getenv('BASE_URL')}api/article"
        
        filter_query = f"keyword={keyword}" if keyword else ""

        if start > 1:
            previous_start = max(1, start - limit)
            previous_query = f"start={previous_start}&limit={limit}"
            pagination_data['previous'] = f"{base_url}?{previous_query}&{filter_query}" if filter_query else f"{base_url}?{previous_query}"
        else:
            pagination_data['previous'] = None

        if start + limit <= total_data:
            next_start = start + limit
            next_query = f"start={next_start}&limit={limit}"
            pagination_data['next'] = f"{base_url}?{next_query}&{filter_query}" if filter_query else f"{base_url}?{next_query}"
        else:
            pagination_data['next'] = None

        final_response = {
            'pagination': pagination_data
        }

        return response.success(final_response)

    except Exception as e:
        print(e)
        return response.serverError([], "Gagal mengambil data artikel.")
