from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import ForeignKey
import re

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    # Keep nullable=False to catch empty-at-DB-time too (no new migration needed if it already exists)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String)

    posts = db.relationship("Post", back_populates="author")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "phone_number": self.phone_number}

    @validates("name")
    def validate_name(self, key, value):
        if value is None or not str(value).strip():
            raise ValueError("Author must have a name.")
        # App-level uniqueness check (no migration/unique index required for the lab)
        existing = Author.query.filter(Author.name == value).first()
        if existing and existing.id != self.id:
            raise ValueError("Author name must be unique.")
        return value.strip()

    @validates("phone_number")
    def validate_phone_number(self, key, value):
        if value is None:
            raise ValueError("Author phone number is required.")
        digits_only = re.sub(r"\D", "", str(value))
        if not re.fullmatch(r"\d{10}", digits_only):
            raise ValueError("Author phone number must be exactly 10 digits.")
        # Store consistently (digits only), or return original if you prefer
        return digits_only


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)

    author_id = db.Column(db.Integer, ForeignKey("authors.id"))
    author = db.relationship("Author", back_populates="posts")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "category": self.category,
            "author_id": self.author_id,
        }

    @validates("content")
    def validate_content(self, key, value):
        if value is None or len(value) < 250:
            raise ValueError("Post content must be at least 250 characters long.")
        return value

    @validates("summary")
    def validate_summary(self, key, value):
        if value is None or len(value) > 250:
            raise ValueError("Post summary must be at most 250 characters.")
        return value

    @validates("category")
    def validate_category(self, key, value):
        allowed = {"Fiction", "Non-Fiction"}
        if value not in allowed:
            raise ValueError("Post category must be either 'Fiction' or 'Non-Fiction'.")
        return value

    @validates("title")
    def validate_title(self, key, value):
        if value is None or not str(value).strip():
            raise ValueError("Post title is required.")
        phrases = ["Won't Believe", "Secret", "Top", "Guess"]
        if not any(phrase in value for phrase in phrases):
            raise ValueError("Post title must be clickbait-y (include Won't Believe, Secret, Top, or Guess).")
        return value.strip()