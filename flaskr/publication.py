from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import sys

bp = Blueprint('publication', __name__)


@bp.route('/publication')
@login_required
def index():
    db = get_db()
    publications = db.execute(
        'SELECT p.publication_id, p.author_id, p.created, p.social_network_src, p.link, p.activated'
        ' FROM publication p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('publication/index.html', publications=publications)


@bp.route('/publication/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        social_network_src = request.form['social_network_src']
        link = request.form['link']
        activated = request.form['activated']
        error = None

        if not link:
            error = 'Publication link is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO publication (author_id, social_network_src, link, activated) VALUES (?, ?, ?, ?)',
                (g.user['id'], social_network_src, link, activated)
            )
            db.commit()
            return redirect(url_for('publication.index'))

    return render_template('publication/create.html')


def get_publication(id, check_author=True):
    publication = get_db().execute(
        'SELECT publication_id, author_id, created, social_network_src, link, activated'
        ' FROM publication publication INNER JOIN user user ON user.id = publication.author_id'
        ' WHERE user.id = ?', (id,)
    ).fetchone()

    if publication is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and publication['author_id'] != g.user['id']:
        abort(403)

    return publication


@bp.route('/publication/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    publication = get_publication(id)

    if request.method == 'POST':
        social_network_src = request.form['social_network_src']
        link = request.form['link']
        activated = request.form['activated']
        error = None

        if not link:
            error = 'Publication link is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE publication SET author_id = ?, social_network_src = ?, link = ?, activated= ?'
                'WHERE publication_id = ?',
                (g.user['id'], social_network_src, link, activated, id)
            )
            db.commit()
            return redirect(url_for('publication.index'))

    return render_template('publication/update.html', publication=publication)


@bp.route('/publication/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    get_publication(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('publication.index'))

