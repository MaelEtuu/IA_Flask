from flask import Blueprint, render_template
from sqlalchemy import func
from extensions import db
from table.table import Artist, Album, Customer, Invoice, Track, InvoiceItem, Genre
from sqlalchemy.orm import aliased
from sqlalchemy import func, select

bdQuestion_bp = Blueprint("bdQuestion", __name__, template_folder="../templates")

@bdQuestion_bp.route("/bdQuestion", methods=["GET"])
def bd():
    q1 = db.session.execute(select(Artist)).scalars().all()

    q2_temp = db.session.query(Artist.ArtistId,Artist.Name,func.count(Album.AlbumId).label('Nombre')).join(Album).group_by(Artist.ArtistId).order_by(func.count(Album.AlbumId).desc()).all()

    q2 = []
    for artist_id, name, nombre in q2_temp:
        albums = db.session.query(Album.Title).filter(Album.ArtistId == artist_id).all()
        q2.append({
            'Name': name,
            'Nombre': nombre,
            'Albums': [a.Title for a in albums]
        })
    q3 = db.session.query(Artist.Name, func.count(Invoice.InvoiceId).label('Nombre de vente')).join(Album, Artist.ArtistId == Album.ArtistId).join(Track, Album.AlbumId == Track.TrackId).join(InvoiceItem, Track.TrackId == InvoiceItem.TrackId).join(Invoice, InvoiceItem.InvoiceId == Invoice.InvoiceId).group_by(Artist.Name).order_by(func.count(Invoice.InvoiceId).desc()).limit(10)

    q4 = db.session.query(Customer.FirstName, Customer.LastName,func.sum(Invoice.Total).label('Total')).join(Invoice, Customer.CustomerId == Invoice.CustomerId).group_by(Customer.FirstName, Customer.LastName).order_by(func.sum(Invoice.Total).desc()).limit(10)

    results = (db.session.query(Genre.Name,func.count(Track.TrackId).label("nb_tracks")).join(Track, Genre.GenreId == Track.GenreId).group_by(Genre.Name).order_by(func.count(Track.TrackId).desc()).all())
    # Préparer les données pour Chart.js
    labels = [r[0] for r in results]
    values = [r[1] for r in results]

    return render_template("bdQuestion.html",
                           artists=q1,
                           artistsq2=q2,
                           clients=q4,
                           labelsPy=labels, 
                           valuesPy=values,
                           artistpop=q3
                           )