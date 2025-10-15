from flask import Blueprint, render_template
from sqlalchemy import func
from extensions import db
from table.table import Artist, Album

bd_bp = Blueprint("bd", __name__, template_folder="../templates")

@bd_bp.route("/bd", methods=["GET"])
def bd():
    artists = Artist.query.all()
    nb = db.session.query(func.count(Artist.ArtistId)).scalar()

    albums = Album.query.all()
    nb2 = db.session.query(func.count(Album.AlbumId)).scalar()

    albumartist = db.session.query(Artist.Name, Album.Title) \
        .join(Album, Artist.ArtistId == Album.ArtistId).all()

    nb3 = db.session.query(func.count(Artist.ArtistId)) \
        .join(Album, Artist.ArtistId == Album.ArtistId) \
        .distinct().scalar()

    return render_template("bd.html",
                           artists=artists,
                           nb=nb,
                           albums=albums,
                           nb2=nb2,
                           albumartist=albumartist,
                           nb3=nb3)