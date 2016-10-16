from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from flask import Flask, render_template, redirect, request
import pg
from wiki_linkify import wiki_linkify
import os

db = pg.DB(
    dbname=os.environ.get('PG_DBNAME'),
    host=os.environ.get('PG_HOST'),
    user=os.environ.get('PG_USERNAME'),
    passwd=os.environ.get('PG_PASSWORD')
)
tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask('Wiki', template_folder=tmp_dir)

@app.route('/')
def home():
    return redirect('/HomePage')

@app.route('/<page_name>')
def view_page(page_name):
    query = db.query("select * from page where title = '%s'" % page_name)
    result_list = query.namedresult()
    if len(result_list) > 0:
        page = result_list[0]
        wiki_linkify_content = wiki_linkify(page.content)
        return render_template(
            'view.html',
            page=page,
            wiki_linkify_content=wiki_linkify_content
        )
    else:
        return render_template(
            'placeholder.html',
            page_name=page_name
        )

@app.route('/<page_name>/edit')
def edit_page(page_name):
    query = db.query("select * from page where title = '%s'" % page_name)
    result_list = query.namedresult()
    if len(result_list) > 0:
        page = result_list[0]
        return render_template(
            'edit.html',
            page_name=page_name,
            page_content=page.content
        )
    else:
        return render_template(
            'edit.html',
            page_name=page_name
        )

@app.route('/<page_name>/save', methods=["POST"])
def save_page(page_name):
    content = request.form.get('content')
    content_column_name = 'content'
    query = db.query("select * from page where title = '%s'" % page_name)
    result_list = query.namedresult()
    if len(result_list) > 0:
        id = result_list[0].id
        db.update('page', {
            'id': id,
            content_column_name: content
        })
    else:
        db.insert('page', title=page_name, content=content)
    return redirect('/%s' % page_name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
