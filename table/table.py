from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from extensions import db

# --- ARTISTS ---
class Artist(db.Model):
    __tablename__ = "artists"
    ArtistId: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(nullable=False)

    albums = relationship("Album", back_populates="artist")

# --- ALBUMS ---
class Album(db.Model):
    __tablename__ = "albums"
    AlbumId: Mapped[int] = mapped_column(primary_key=True)
    Title: Mapped[str] = mapped_column(nullable=False)
    ArtistId: Mapped[int] = mapped_column(ForeignKey("artists.ArtistId"))

    artist = relationship("Artist", back_populates="albums")
    tracks = relationship("Track", back_populates="album")

# --- CUSTOMERS ---
class Customer(db.Model):
    __tablename__ = "customers"
    CustomerId: Mapped[int] = mapped_column(primary_key=True)
    FirstName: Mapped[str] = mapped_column(nullable=False)
    LastName: Mapped[str] = mapped_column(nullable=False)
    Company: Mapped[str]
    Address: Mapped[str]
    City: Mapped[str]
    State: Mapped[str]
    Country: Mapped[str]
    PostalCode: Mapped[str]
    Phone: Mapped[str]
    Fax: Mapped[str]
    Email: Mapped[str] = mapped_column(nullable=False)
    SupportRepId: Mapped[int] = mapped_column(ForeignKey("employees.EmployeeId"))

    support_rep = relationship("Employee", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer")

# --- EMPLOYEES ---
class Employee(db.Model):
    __tablename__ = "employees"
    EmployeeId: Mapped[int] = mapped_column(primary_key=True)
    LastName: Mapped[str] = mapped_column(nullable=False)
    FirstName: Mapped[str] = mapped_column(nullable=False)
    Title: Mapped[str]
    ReportsTo: Mapped[int] = mapped_column(ForeignKey("employees.EmployeeId"))
    BirthDate: Mapped[str]
    HireDate: Mapped[str]
    Address: Mapped[str]
    City: Mapped[str]
    State: Mapped[str]
    Country: Mapped[str]
    PostalCode: Mapped[str]
    Phone: Mapped[str]
    Fax: Mapped[str]
    Email: Mapped[str]

    manager = relationship("Employee", remote_side=[EmployeeId], back_populates="subordinates")
    subordinates = relationship("Employee", back_populates="manager")
    customers = relationship("Customer", back_populates="support_rep")

# --- GENRES ---
class Genre(db.Model):
    __tablename__ = "genres"
    GenreId: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str]

    tracks = relationship("Track", back_populates="genre")

# --- INVOICES ---
class Invoice(db.Model):
    __tablename__ = "invoices"
    InvoiceId: Mapped[int] = mapped_column(primary_key=True)
    CustomerId: Mapped[int] = mapped_column(ForeignKey("customers.CustomerId"))
    InvoiceDate: Mapped[str]
    BillingAddress: Mapped[str]
    BillingCity: Mapped[str]
    BillingState: Mapped[str]
    BillingCountry: Mapped[str]
    BillingPostalCode: Mapped[str]
    Total: Mapped[float]

    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")

# --- INVOICE ITEMS ---
class InvoiceItem(db.Model):
    __tablename__ = "invoice_items"
    InvoiceLineId: Mapped[int] = mapped_column(primary_key=True)
    InvoiceId: Mapped[int] = mapped_column(ForeignKey("invoices.InvoiceId"))
    TrackId: Mapped[int] = mapped_column(ForeignKey("tracks.TrackId"))
    UnitPrice: Mapped[float]
    Quantity: Mapped[int]

    invoice = relationship("Invoice", back_populates="items")
    track = relationship("Track", back_populates="invoice_items")

# --- MEDIA TYPES ---
class MediaType(db.Model):
    __tablename__ = "media_types"
    MediaTypeId: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str]

    tracks = relationship("Track", back_populates="media_type")

# --- PLAYLISTS ---
class Playlist(db.Model):
    __tablename__ = "playlists"
    PlaylistId: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str]

    tracks = relationship("PlaylistTrack", back_populates="playlist")

# --- PLAYLIST_TRACK ---
class PlaylistTrack(db.Model):
    __tablename__ = "playlist_track"
    PlaylistId: Mapped[int] = mapped_column(ForeignKey("playlists.PlaylistId"), primary_key=True)
    TrackId: Mapped[int] = mapped_column(ForeignKey("tracks.TrackId"), primary_key=True)

    playlist = relationship("Playlist", back_populates="tracks")
    track = relationship("Track", back_populates="playlists")

# --- TRACKS ---
class Track(db.Model):
    __tablename__ = "tracks"
    TrackId: Mapped[int] = mapped_column(primary_key=True)
    Name: Mapped[str] = mapped_column(nullable=False)
    AlbumId: Mapped[int] = mapped_column(ForeignKey("albums.AlbumId"))
    MediaTypeId: Mapped[int] = mapped_column(ForeignKey("media_types.MediaTypeId"))
    GenreId: Mapped[int] = mapped_column(ForeignKey("genres.GenreId"))
    Composer: Mapped[str]
    Milliseconds: Mapped[int]
    Bytes: Mapped[int]
    UnitPrice: Mapped[float]

    album = relationship("Album", back_populates="tracks")
    media_type = relationship("MediaType", back_populates="tracks")
    genre = relationship("Genre", back_populates="tracks")
    invoice_items = relationship("InvoiceItem", back_populates="track")
    playlists = relationship("PlaylistTrack", back_populates="track")