from flask import Flask, render_template, redirect, url_for, jsonify, session, request, send_from_directory
from flask_paginate import Pagination, get_page_args
import mysqlDB as msq
import secrets
from datetime import datetime
import requests
import random
import re

from flask_session import Session

# import pandas as pd

# def excel_to_csv(excel_file, csv_file):
#     # Wczytaj plik Excel
#     df = pd.read_excel(excel_file)
    
#     # Zapisz do pliku CSV
#     df.to_csv(csv_file, index=False)

# Przykład użycia:
# excel_to_csv('plik.xlsx', 'plik.csv')

app = Flask(__name__)
msq.init_app(app)
app.config['PER_PAGE'] = 4
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'  # Możesz wybrać inny backend, np. 'redis', 'sqlalchemy', itp.
Session(app)

def getLangText(text, dest="en", source="pl"):
    if not text:
        return text
    # bezpiecznik: nie tłumacz "ścian"
    if len(text) > 8000:
        return text
    try:
        r = requests.post(
            "http://127.0.0.1:5055/translate",
            json={"text": text, "source": source, "target": dest, "format": "text"},
            timeout=(2, 8),
        )
        r.raise_for_status()
        return r.json().get("text", text)
    except Exception as e:
        print(f"Exception Error: {e}")
        return text

def format_date(date_input, pl=True):
    ang_pol = {
        'January': 'styczeń',
        'February': 'luty',
        'March': 'marzec',
        'April': 'kwiecień',
        'May': 'maj',
        'June': 'czerwiec',
        'July': 'lipiec',
        'August': 'sierpień',
        'September': 'wrzesień',
        'October': 'październik',
        'November': 'listopad',
        'December': 'grudzień'
    }
    # Sprawdzenie czy data_input jest instancją stringa; jeśli nie, zakładamy, że to datetime
    if isinstance(date_input, str):
        date_object = datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S')
    else:
        # Jeśli date_input jest już obiektem datetime, używamy go bezpośrednio
        date_object = date_input

    formatted_date = date_object.strftime('%d %B %Y')
    if pl:
        for en, pl in ang_pol.items():
            formatted_date = formatted_date.replace(en, pl)

    return formatted_date


# Funkcja pobierania oferty z pliku csv
def get_offers_from_csv(filename='oferta-sprzet.csv'):
    with open(filename, 'r', encoding='utf-8') as file:
        file_to_list = file.readlines()
    export = {}
    for line in file_to_list[1:]:
        line = line.strip().split(';')
        try:int(float(line[9]))
        except ValueError:line[9] = 'None'
        theme = {
            "id": line[0],
            "marka": None if line[1] == 'None' else line[1],
            "symbol": None if line[2] == 'None' else line[2],
            "kategoria": None if line[3] == 'None' else line[3],
            "opcja": None if line[4] == 'None' else line[4],
            "udzwig-max": None if line[5] == 'None' else line[5],
            "udzwig-min": None if line[6] == 'None' else line[6],
            "zasieg": None if line[7] == 'None' else line[7],
            "cena-mc": None if line[8] == 'None' else line[8],
            "cena-12xh": None if line[9] == 'None' else int(float(line[9])),
            "cena-godzina": None if line[10] == 'None' else line[10],
            "oferta-na-godziny": None if line[11] == 'None' else line[11],
            "oferta-na-mc": None if line[12] == 'None' else line[12],
            "oferta-na-dzien": None if line[13] == 'None' else line[13],
            "opis": None if line[14] == 'None' else line[14],
            "przeznaczenie": None if line[15] == 'None' else line[15],
            "warunki-wynajmu": None if line[16] == 'None' else line[16],
            "podsumowanie": None if line[17] == 'None' else line[17],
            "oferta-wynajmu": None if line[18] == 'None' else line[18],
            "foto": None if line[19] == 'None' else line[19],
            "foto-list": None if line[20] == 'None' else line[20],
            "homepage": 0 if line[21] == 'None' else int(line[21])
        }
        export[line[0]] = theme
    return export

#  Funkcja pobiera dane z bazy danych 
def take_data_where_ID(key, table, id_name, ID):
    dump_key = msq.connect_to_database(f'SELECT {key} FROM {table} WHERE {id_name} = {ID};')
    return dump_key

def take_data_table(key, table):
    dump_key = msq.connect_to_database(f'SELECT {key} FROM {table};')
    return dump_key

def generator_subsDataDB():
    subsData = []
    took_subsD = take_data_table('*', 'newsletter')
    for data in took_subsD:
        if data[4] != 1: continue
        ID = data[0]
        theme = {
            'id': ID, 
            'email':data[2],
            'name':data[1], 
            'status': str(data[4]), 
            }
        subsData.append(theme)
    return subsData

def _blog_rows(limit=None, post_id=None, detailed=False, offset=0, cards=False, post_ids=None):
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError('offset must be a non-negative integer')
    if offset and limit is None:
        raise ValueError('offset requires a limit')
    columns = [
        ('p.ID', 'post_id'), ('c.ID', 'id'), ('c.TITLE', 'title'),
        ('c.HIGHLIGHTS', 'highlight'), ('c.HEADER_FOTO', 'mainFoto'),
        ('c.CATEGORY', 'category'), ('c.DATE_TIME', 'data'),
        ('a.NAME_AUTHOR', 'author'),
    ]
    if cards and not detailed:
        columns += [('c.TAGS', 'tags'), ('c.CONTENT_FOTO', 'contentFoto')]
    if detailed:
        columns += [
            ('c.CONTENT_MAIN', 'introduction'), ('c.CONTENT_FOTO', 'contentFoto'),
            ('c.BULLETS', 'additionalList'), ('c.TAGS', 'tags'),
            ('a.ABOUT_AUTHOR', 'author_about'), ('a.AVATAR_AUTHOR', 'author_avatar'),
            ('a.FACEBOOK', 'author_facebook'), ('a.TWITER_X', 'author_twitter'),
            ('a.INSTAGRAM', 'author_instagram'),
        ]
    query = 'SELECT ' + ', '.join(column for column, _ in columns)
    query += """
        FROM blog_posts p
        LEFT JOIN contents c ON c.ID = p.CONTENT_ID
        LEFT JOIN authors a ON a.ID = p.AUTHOR_ID
    """
    params = []
    if post_id is not None:
        query += ' WHERE p.ID = %s'
        params.append(post_id)
    if post_ids is not None:
        if not post_ids:
            return []
        query += (' AND ' if post_id is not None else ' WHERE ')
        query += 'p.ID IN (' + ', '.join(['%s'] * len(post_ids)) + ')'
        params.extend(post_ids)
    query += ' ORDER BY p.ID DESC'
    if limit is not None:
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            raise ValueError('limit must be a non-negative integer')
        query += ' LIMIT %s'
        params.append(limit)
        if offset:
            query += ' OFFSET %s'
            params.append(offset)
    rows = msq.safe_connect_to_database(query, tuple(params))
    return [dict(zip((key for _, key in columns), row)) for row in rows]


def _blog_theme(row, lang):
    theme = {key: value for key, value in row.items() if key != 'post_id'}
    if lang != 'pl':
        for key in ('title', 'highlight', 'category', 'introduction',
                    'additionalList', 'tags', 'author_about'):
            if key in theme:
                theme[key] = getLangText(theme[key])
    theme['data'] = format_date(theme['data'], lang == 'pl')
    if 'additionalList' in theme:
        bullets = str(theme['additionalList'])
        if lang != 'pl':
            bullets = bullets.replace('#SPLX#', '#splx#')
        theme['additionalList'] = bullets.split('#splx#')
    if 'tags' in theme:
        theme['tags'] = str(theme['tags']).split(', ')
    return theme


def _blog_details(lang='pl', post_id=None):
    rows = _blog_rows(post_id=post_id, detailed=True)
    if not rows:
        return []
    # Fetch comments and their authors once for the whole selected collection.
    query = """
        SELECT com.*, n.CLIENT_NAME, n.CLIENT_EMAIL, n.AVATAR_USER, stats.comment_count
        FROM comments com
        JOIN blog_posts p ON p.ID = com.BLOG_POST_ID
        LEFT JOIN newsletter n ON n.ID = com.AUTHOR_OF_COMMENT_ID
        LEFT JOIN (
            SELECT AUTHOR_OF_COMMENT_ID, COUNT(*) AS comment_count
            FROM comments GROUP BY AUTHOR_OF_COMMENT_ID
        ) stats ON stats.AUTHOR_OF_COMMENT_ID = com.AUTHOR_OF_COMMENT_ID
    """
    params = ()
    if post_id is not None:
        query += ' WHERE p.ID = %s'
        params = (post_id,)
    query += ' ORDER BY com.ID'
    comments = {}
    for com in msq.safe_connect_to_database(query, params):
        post_comments = comments.setdefault(com[1], {})
        post_comments[len(post_comments)] = {
            'id': com[0],
            'message': com[2] if lang == 'pl' else getLangText(com[2]),
            'user': com[-4], 'e-mail': com[-3], 'avatar': com[-2],
            'data-time': format_date(com[4], lang == 'pl'),
        }
        if post_id is not None:
            count = com[-1] or 0
            bonus = 4 if count > 10 else 2 if count > 4 else 1 if count > 1 else 0
            post_comments[len(post_comments) - 1]['user_stars'] = 1 + bool(com[-2]) + bonus
    result = []
    for row in rows:
        theme = _blog_theme(row, lang)
        theme['comments'] = comments.get(row['post_id'], {})
        result.append(theme)
    return result


def generator_daneDBList(lang='pl'):
    return _blog_details(lang)


def generator_daneDBList_short(lang='pl', limit=None, offset=0):
    # Unlimited by default: the home page explicitly requests only three rows.
    return [_blog_theme(row, lang) for row in _blog_rows(limit=limit, offset=offset)]


def _blog_count():
    rows = msq.connect_to_database('SELECT COUNT(*) FROM blog_posts')
    return rows[0][0] if rows else 0


def generator_daneDBList_cetegory():
    took_allPost = msq.connect_to_database('SELECT CATEGORY FROM contents ORDER BY ID DESC;')
    cat_count = {}
    for (category,) in took_allPost:
        cat_count[category] = cat_count.get(category, 0) + 1
    return [f"{cat} ({count})" for cat, count in cat_count.items()], cat_count


def generator_daneDBList_RecentPosts(main_id, amount=3):
    # Preserve the existing random selection of suggested posts.
    rows = msq.safe_connect_to_database(
        'SELECT ID FROM contents WHERE ID != %s ORDER BY ID DESC', (main_id,))
    ids = [row[0] for row in rows]
    return random.sample(ids, min(amount, len(ids)))


def generator_daneDBList_one_post_id(id_post, lang='pl'):
    return _blog_details(lang, post_id=id_post)


def _blog_page(limit, offset, lang='pl'):
    return [_blog_theme(row, lang) for row in _blog_rows(limit=limit, offset=offset, cards=True)]


def _blog_recent_posts(main_id, amount=3, lang='pl'):
    ids = generator_daneDBList_RecentPosts(main_id, amount)
    rows = {row['post_id']: row for row in _blog_rows(post_ids=ids, cards=True)}
    return [_blog_theme(rows[post_id], lang) for post_id in ids if post_id in rows]


def is_valid_phone(phone):
    # Wzorzec dla numeru telefonu: zaczyna się opcjonalnym plusem, po którym następuje 9-15 cyfr
    pattern = re.compile(r'^\+?\d{9,15}$')
    
    if pattern.match(phone):
        return True
    else:
        return False

############################
##      ######           ###
##      ######           ###
##     ####              ###
##     ####              ###
##    ####               ###
##    ####               ###
##   ####                ###
##   ####                ###
#####                    ###
#####                    ###
##   ####                ###
##   ####                ###
##    ####               ###
##    ####               ###
##     ####              ###
##     ####              ###
##      ######           ###
##      ######           ###
############################

# @app.route('/.well-known/pki-validation/certum.txt')
# def download_file():
#     return send_from_directory(app.root_path, 'certum.txt')

@app.template_filter('smart_truncate')
def smart_truncate(content, length=400):
    if len(content) <= length:
        return content
    else:
        # Znajdujemy miejsce, gdzie jest koniec pełnego słowa, nie przekraczając maksymalnej długości
        truncated_content = content[:length].rsplit(' ', 1)[0]
        return f"{truncated_content}..."

def get_latest_blog_posts(lang='pl'):
    return [
        {key: post[key] for key in ('id', 'title', 'data')}
        for post in generator_daneDBList_short(lang, limit=2)
    ]


@app.context_processor
def inject_footer_data():
    # Dodaj dane do kontekstu szablonu, aby były dostępne we wszystkich widokach
    return {
        'latest_blog_posts': get_latest_blog_posts()
    }

@app.route('/')
def index():
    session['page'] = 'index'
    pageTitle = 'Strona Główna'
       
    if f'BLOG-SHORT' not in session:
        blog_post = generator_daneDBList_short(limit=2)
        session[f'BLOG-SHORT'] = blog_post
    else:
        blog_post = session[f'BLOG-SHORT']
    
    blog_post_two = []
    for i, member in enumerate(blog_post):
        if  i < 2: blog_post_two.append(member)

    cala_oferta = get_offers_from_csv()
    oferta = []
    for item in cala_oferta.values():
        if item['homepage'] == 1:
            oferta.append(item)

    return render_template(
        f'index.html',
        pageTitle=pageTitle,
        blog_post_two=blog_post_two,
        oferta=oferta
        )

@app.route('/oferta-sprzetu')
def naszaOfertaSprzet():
    session['page'] = 'Nasza Oferta'
    pageTitle = 'Nasza Oferta'

    selected_filter = request.args.get('filter', '*')
    cala_oferta = get_offers_from_csv()
    oferta = []

    for item in cala_oferta.values():
        if item['kategoria'] == 'HDS':
            item['class'] = 'hds'
        elif item['kategoria'] == 'Wywrotki':
            item['class'] = 'wywrotki'
        elif item['kategoria'] == 'Ciągniki Siodłowe':
            item['class'] = 'siodlowe'
        elif item['kategoria'] == 'Naczepy':
            item['class'] = 'naczepy'
        elif item['kategoria'] == 'Dźwigi':
            item['class'] = 'dzwigi'
        elif item['kategoria'] == 'Koparki':
            item['class'] = 'koparki'
        elif item['kategoria'] == 'Ładowarki':
            item['class'] = 'ladowarki'
        elif item['kategoria'] == 'Zagęszczarki':
            item['class'] = 'zageszczarki'
        else:
            item['class'] = ''

        if item['opcja'] is not None and item['opcja'] == 'HDS':
            item['class'] += ' hds'
        elif item['opcja'] is not None and item['opcja'] == 'Wywrotki':
            item['class'] += ' wywrotki'
        elif item['opcja'] is not None and item['opcja'] == 'Ciągniki Siodłowe':
            item['class'] += ' siodlowe'
        elif item['opcja'] is not None and item['opcja'] == 'Naczepy':
            item['class'] += ' naczepy'
        elif item['opcja'] is not None and item['opcja'] == 'Dźwigi':
            item['class'] += ' dzwigi'
        elif item['opcja'] is not None and item['opcja'] == 'Koparki':
            item['class'] += ' koparki'
        elif item['opcja'] is not None and item['opcja'] == 'Ładowarki':
            item['class'] += ' ladowarki'
        elif item['opcja'] is not None and item['opcja'] == 'Zagęszczarki':
            item['class'] += ' zageszczarki'
        
        oferta.append(item)
    

    return render_template(
        f'oferta-sprzet.html',
        pageTitle=pageTitle,
        selected_filter=selected_filter,
        oferta=oferta
        )

@app.route('/sprzet-specyfikacja')
def sprzetSpecyfikacja():
    session['page'] = 'Specyfikacja sprzętu'

    id_oferty = request.args.get('setoffer', None)
    cala_oferta = get_offers_from_csv()

    if id_oferty is None or not id_oferty in cala_oferta: 
        return redirect(url_for(f'naszaOfertaSprzet'))
    else:
        specyfikacja = cala_oferta[id_oferty]
        nazwa_sprzetu = specyfikacja['marka']

    pageTitle = f'Specyfikacja sprzętu {nazwa_sprzetu}'

    return render_template(
        f'sprzet-specyfikacja.html',
        pageTitle=pageTitle,
        specyfikacja=specyfikacja
        )

@app.route('/o-nas')
def oNas():
    session['page'] = 'O Nas'
    pageTitle = 'O Nas'

    return render_template(
        f'o-nas.html',
        pageTitle=pageTitle
        )

@app.route('/uslugi')
def uslugi():
    session['page'] = 'Nasze usługi'
    pageTitle = 'Nasze usługi'

    return render_template(
        f'oferta-uslug.html',
        pageTitle=pageTitle
        )

@app.route('/kontakt')
def kontakt():
    session['page'] = 'kontakt'
    pageTitle = 'kontakt'

    nazwa_oferty = request.args.get('settitle', '')


    return render_template(
        f'kontakt.html',
        pageTitle=pageTitle,
        nazwa_oferty=nazwa_oferty
        )

@app.route('/blog')
def blogs():
    session['page'] = 'blogs'
    pageTitle = 'Blog'

    # Discard the old full-blog session cache; fetch only this page from SQL.
    session.pop('blog_post', None)
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    page = max(1, page)
    per_page = max(1, per_page)
    offset = (page - 1) * per_page
    total = _blog_count()
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    posts = _blog_page(per_page, offset)

    cats = generator_daneDBList_cetegory()
    cat_dict = cats[1]
    recentPosts = _blog_recent_posts(0)
    
    # print(posts)
    tag_set = set()
    for post_dict in posts:
        if 'tags' in post_dict:
            for tag in post_dict['tags']:
                tag_set.add(tag)
    tag_list = [str(t).replace('#', '') for t in tag_set]

    return render_template(
        f'blog.html',
        pageTitle=pageTitle,
        cat_dict=cat_dict,
        recentPosts=recentPosts,
        pagination=pagination,
        posts=posts,
        tag_list=tag_list
        )

@app.route('/blog-one', methods=['GET'])
def blogOne():
    session['page'] = 'blogOne'
    
    if 'post' in request.args:
        post_id = request.args.get('post')
        try: post_id_int = int(post_id)
        except ValueError: return redirect(url_for('blogs'))
    else:
        return redirect(url_for(f'blogs'))
    
    choiced = generator_daneDBList_one_post_id(post_id_int)[0]
    choiced['len'] = len(choiced['comments'])
    pageTitle = choiced['title']

    cats = generator_daneDBList_cetegory()
    cat_dict = cats[1]
    recentPosts = _blog_recent_posts(post_id_int)

    return render_template(
        f'blog-one.html',
        pageTitle=pageTitle,
        choiced=choiced,
        cat_dict=cat_dict,
        recentPosts=recentPosts
        )


@app.errorhandler(404)
def page_not_found(e):
    # Tutaj możesz przekierować do dowolnej trasy, którą chcesz wyświetlić jako stronę błędu 404.
    return redirect(url_for(f'index'))


@app.route('/find-by-category', methods=['GET'])
def findByCategory():

    query = request.args.get('category')
    if not query:
        if not 'last_search' in session:
            print('Błąd requesta')
            return redirect(url_for('index'))
        else:
            query = session['last_search']
    else:
        session['last_search'] = query
        
    sqlQuery = """
                SELECT ID FROM contents 
                WHERE CATEGORY LIKE %s 
                ORDER BY ID DESC;
                """
    params = (f'%{query}%', )
    results = msq.safe_connect_to_database(sqlQuery, params)
    pageTitle = f'Wyniki wyszukiwania dla categorii {query}'

    searchResults = []
    for find_id in results:
        post_id = int(find_id[0])
        t_post = generator_daneDBList_one_post_id(post_id)[0]
        theme = {
            'id': t_post['id'],
            'title': t_post['title'],
            'mainFoto': t_post['mainFoto'],
            'introduction': smart_truncate(t_post['introduction'], 200),
            'category': t_post['category'],
            'author': t_post['author'],
            'data': t_post['data']
        }
        searchResults.append(theme)

    found = len(searchResults)

    # Ustawienia paginacji
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = len(searchResults)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    # Pobierz tylko odpowiednią ilość postów na aktualnej stronie
    posts = searchResults[offset: offset + per_page]


    return render_template(
        "searchBlog.html",
        pageTitle=pageTitle,
        posts=posts,
        found=found,
        pagination=pagination
        )

@app.route('/find-by-tags', methods=['GET'])
def findByTags():

    query = request.args.get('tag')

    if not query:
        if not 'last_search' in session:
            print('Błąd requesta')
            return redirect(url_for('index'))
        else:
            query = session['last_search']
    else:
        session['last_search'] = query

    sqlQuery = """
                SELECT ID FROM contents 
                WHERE TAGS LIKE %s 
                ORDER BY ID DESC;
                """
    params = (f'%#{query}%', )
    results = msq.safe_connect_to_database(sqlQuery, params)
    pageTitle = f'Wyniki wyszukiwania dla tagu {query}'

    searchResults = []
    for find_id in results:
        post_id = int(find_id[0])
        t_post = generator_daneDBList_one_post_id(post_id)[0]
        theme = {
            'id': t_post['id'],
            'title': t_post['title'],
            'mainFoto': t_post['mainFoto'],
            'introduction': smart_truncate(t_post['introduction'], 200),
            'category': t_post['category'],
            'author': t_post['author'],
            'data': t_post['data']
        }
        searchResults.append(theme)

    found = len(searchResults)

    # Ustawienia paginacji
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = len(searchResults)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    # Pobierz tylko odpowiednią ilość postów na aktualnej stronie
    posts = searchResults[offset: offset + per_page]


    return render_template(
        "searchBlog.html",
        pageTitle=pageTitle,
        posts=posts,
        found=found,
        pagination=pagination,
        query=query
        )


@app.route('/search-post-blog', methods=['GET', 'POST']) #, methods=['GET', 'POST']
def searchBlog():
    if request.method == "POST":
        query = request.form["query"]
        if query == '':
            print('Błąd requesta')
            return redirect(url_for('index'))
        
        session['last_search'] = query
    elif 'last_search' in session:
        query = session['last_search']
    else:
        print('Błąd requesta')
        return redirect(url_for('index'))  # Uwaga: poprawiłem 'f' na 'index'

    sqlQuery = """
                SELECT ID FROM contents 
                WHERE TITLE LIKE %s 
                OR CONTENT_MAIN LIKE %s 
                OR HIGHLIGHTS LIKE %s 
                OR BULLETS LIKE %s 
                ORDER BY ID DESC;
                """
    params = (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%')
    results = msq.safe_connect_to_database(sqlQuery, params)
    pageTitle = f'Wyniki wyszukiwania dla {query}'

    searchResults = []
    for find_id in results:
        post_id = int(find_id[0])
        t_post = generator_daneDBList_one_post_id(post_id)[0]
        theme = {
            'id': t_post['id'],
            'title': t_post['title'],
            'mainFoto': t_post['mainFoto'],
            'introduction': smart_truncate(t_post['introduction'], 200),
            'category': t_post['category'],
            'author': t_post['author'],
            'data': t_post['data']
        }
        searchResults.append(theme)

    found = len(searchResults)

    # Ustawienia paginacji
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = len(searchResults)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    # Pobierz tylko odpowiednią ilość postów na aktualnej stronie
    posts = searchResults[offset: offset + per_page]


    return render_template(
        "searchBlog.html",
        pageTitle=pageTitle,
        posts=posts,
        found=found,
        pagination=pagination
        )

@app.route('/send-mess-pl', methods=['POST'])
def sendMess():

    if request.method == 'POST':
        form_data = request.json
        CLIENT_NAME = form_data['name']
        CLIENT_SUBJECT = form_data['subject']
        CLIENT_EMAIL = form_data['email']
        CLIENT_MESSAGE = form_data['message']

        if 'condition' not in form_data:
            return jsonify(
                {
                    'success': False, 
                    'message': f'Musisz zaakceptować naszą politykę prywatności!'
                })
        if CLIENT_NAME == '':
            return jsonify(
                {
                    'success': False, 
                    'message': f'Musisz podać swoje Imię i Nazwisko!'
                })
        if CLIENT_SUBJECT == '':
            return jsonify(
                {
                    'success': False, 
                    'message': f'Musisz podać temat wiadomości!'
                })
        if CLIENT_EMAIL == '' or '@' not in CLIENT_EMAIL or '.' not in CLIENT_EMAIL or len(CLIENT_EMAIL) < 7:
            return jsonify(
                {
                    'success': False, 
                    'message': f'Musisz podać adres email!'
                })
        if CLIENT_MESSAGE == '':
            return jsonify(
                {
                    'success': False, 
                    'message': f'Musisz podać treść wiadomości!'
                })

        # --- meta z żądania (Flask/FastAPI) ---
        ref = request.headers.get('Referer')
        ua  = request.headers.get('User-Agent')
        # Host: w Flask jest też request.host; w FastAPI/Starlette z ASGI bywa tylko nagłówek
        host = request.headers.get('Host') or getattr(request, 'host', None)

        # Realne IP z uwzględnieniem proxy/CDN:
        xff = request.headers.get('X-Forwarded-For', '')
        ip_from_xff = xff.split(',')[0].strip() if xff else None
        ip = (request.headers.get('CF-Connecting-IP') or ip_from_xff or request.remote_addr)

        zapytanie_sql = '''
            INSERT INTO contact 
                (CLIENT_NAME, CLIENT_EMAIL, SUBJECT, MESSAGE, DONE, remote_ip, referer, user_agent, source_host) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''
        dane = (
            CLIENT_NAME,
            CLIENT_EMAIL,
            CLIENT_SUBJECT,
            CLIENT_MESSAGE,
            1,
            ip,
            ref,
            ua,
            host
        )
    
        if msq.insert_to_database(zapytanie_sql, dane):
            return jsonify(
                {
                    'success': True, 
                    'message': f'Wiadomość została wysłana!'
                })
        else:
            return jsonify(
                {
                    'success': False, 
                    'message': f'Wystąpił problem z wysłaniem Twojej wiadomości, skontaktuj się w inny sposób lub spróbuj później!'
                })

    return redirect(url_for('index'))


@app.route('/ask-phone', methods=['POST'])
def askPhone():
    try:
        form_data = request.json
        CLIENT_PHONE = form_data['phone']

        if CLIENT_PHONE == '' or not is_valid_phone(CLIENT_PHONE):
            return jsonify({
                'success': False,
                'message': 'Musisz podać poprawny numer telefonu!'
            })

        CLIENT_NAME = 'Użytkownik strony DMD Transport'
        CLIENT_EMAIL = 'brak@adresu.email'
        CLIENT_SUBJECT = 'Prośba o kontakt ze strony DMD Transport'
        CLIENT_MESSAGE = f'Proszę o kontakt {CLIENT_PHONE}'

        # --- meta z żądania (Flask/FastAPI) ---
        ref = request.headers.get('Referer')
        ua  = request.headers.get('User-Agent')
        # Host: w Flask jest też request.host; w FastAPI/Starlette z ASGI bywa tylko nagłówek
        host = request.headers.get('Host') or getattr(request, 'host', None)

        # Realne IP z uwzględnieniem proxy/CDN:
        xff = request.headers.get('X-Forwarded-For', '')
        ip_from_xff = xff.split(',')[0].strip() if xff else None
        ip = (request.headers.get('CF-Connecting-IP') or ip_from_xff or request.remote_addr)

        zapytanie_sql = '''
            INSERT INTO contact 
                (CLIENT_NAME, CLIENT_EMAIL, SUBJECT, MESSAGE, DONE, remote_ip, referer, user_agent, source_host) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''
        dane = (
            CLIENT_NAME,
            CLIENT_EMAIL,
            CLIENT_SUBJECT,
            CLIENT_MESSAGE,
            1,
            ip,
            ref,
            ua,
            host
        )

        if msq.insert_to_database(zapytanie_sql, dane):
            return jsonify({
                'success': True,
                'message': 'Numer został wysłany!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Wystąpił problem z wysłaniem numeru telefonu!'
            })

    except Exception as e:
        # Zaloguj błąd po stronie serwera (opcjonalnie)
        print(f'Błąd: {e}')
        return jsonify({
            'success': False,
            'message': 'Wewnętrzny błąd serwera. Spróbuj ponownie później.'
        }), 500
    

@app.route('/add-subs-pl', methods=['POST'])
def addSubs():
    subsList = generator_subsDataDB() # pobieranie danych subskrybentów

    if request.method == 'POST':
        form_data = request.json

        SUB_NAME = form_data['Imie']
        SUB_EMAIL = form_data['Email']
        USER_HASH = secrets.token_hex(20)

        allowed = True
        for subscriber in subsList:
            if subscriber['email'] == SUB_EMAIL:
                allowed = False

        if allowed:
            # --- meta z żądania (Flask/FastAPI) ---
            ref = request.headers.get('Referer')
            ua  = request.headers.get('User-Agent')
            host = request.headers.get('Host') or getattr(request, 'host', None)

            # Realne IP z uwzględnieniem proxy/CDN:
            xff = request.headers.get('X-Forwarded-For', '')
            ip_from_xff = xff.split(',')[0].strip() if xff else None
            ip = (request.headers.get('CF-Connecting-IP') or ip_from_xff or request.remote_addr)

            # (opcjonalnie) bardzo prosty anty-bot: wymagaj swojej domeny w referer + niepusty UA
            # if (not ua or not ua.strip()) or (ref and 'dmdbudownictwo.pl' not in ref):
            #     abort(403)

            zapytanie_sql = '''
                INSERT INTO newsletter 
                    (CLIENT_NAME, CLIENT_EMAIL, ACTIVE, USER_HASH, remote_ip, referer, user_agent, source_host) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            '''
            dane = (SUB_NAME, SUB_EMAIL, 0, USER_HASH, ip, ref, ua, host)
            if msq.insert_to_database(zapytanie_sql, dane):
                return jsonify(
                    {
                        'success': True, 
                        'message': f'Zgłoszenie nowego subskrybenta zostało wysłane, aktywuj przez email!'
                    })
            else:
                return jsonify(
                {
                    'success': False, 
                    'message': f'Niestety nie udało nam się zarejestrować Twojej subskrypcji z powodu niezidentyfikowanego błędu!'
                })
        else:
            return jsonify(
                {
                    'success': False, 
                    'message': f'Podany adres email jest już zarejestrowany!'
                })
    return redirect(url_for('index'))

@app.route('/add-comm-pl', methods=['POST'])
def addComm():
    subsList = generator_subsDataDB() # pobieranie danych subskrybentów

    if request.method == 'POST':
        form_data = request.json
        # print(form_data)
        SUB_ID = None
        SUB_NAME = form_data['Name']
        SUB_EMAIL = form_data['Email']
        SUB_COMMENT = form_data['Comment']
        POST_ID = form_data['id']
        allowed = False
        for subscriber in subsList:
            if subscriber['email'] == SUB_EMAIL and subscriber['name'] == SUB_NAME and int(subscriber['status']) == 1:
                allowed = True
                SUB_ID = subscriber['id']
                break
        if allowed and SUB_ID:
            # print(form_data)
            zapytanie_sql = '''
                    INSERT INTO comments 
                        (BLOG_POST_ID, COMMENT_CONNTENT, AUTHOR_OF_COMMENT_ID) 
                        VALUES (%s, %s, %s);
                    '''
            dane = (POST_ID, SUB_COMMENT, SUB_ID)
            if msq.insert_to_database(zapytanie_sql, dane):
                return jsonify({'success': True, 'message': f'Post został skomentowany!'})
        else:
            return jsonify({'success': False, 'message': f'Musisz być naszym subskrybentem żeby komentować naszego bloga!'})

    return redirect(url_for('blogs'))

@app.route('/subpage', methods=['GET'])
def subpage():
    session['page'] = 'subpage'
    pageTitle = 'subpage'

    if 'target' in request.args:
        if request.args['target'] in ['polityka', 'zasady', 'pomoc']:
            targetPage = request.args['target']
            pageTitle = targetPage
        else: 
            targetPage = "pomoc"
            pageTitle = targetPage
    else:
        targetPage = "pomoc"
        pageTitle = targetPage

    return render_template(
        f'{targetPage}.html',
        pageTitle=pageTitle
        )



if __name__ == '__main__':
    # app.run(debug=True, port=5070)
    app.run(debug=True, host='0.0.0.0', port=5070)