from flask_sqlalchemy import SQLAlchemy

# Import db locally to avoid circular import
def get_db():
    from app import db
    return db

class FileManagement(get_db().Model):
    id = get_db().Column(get_db().Integer, primary_key=True)
    name = get_db().Column(get_db().String(255), nullable=False)
    filename = get_db().Column(get_db().String(255), nullable=False, unique=True)
    filepath = get_db().Column(get_db().String(255), nullable=False)
    file_type = get_db().Column(get_db().String(255), nullable=False) # cls, detect
    description = get_db().Column(get_db().Text, nullable=True)
    created_at = get_db().Column(get_db().DateTime, server_default=get_db().func.now())
    updated_at = get_db().Column(get_db().DateTime, server_default=get_db().func.now(), server_onupdate=get_db().func.now())


    def __repr__(self):
        return f'<FileManagement {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'filename': self.filename,
            'filepath': self.filepath,
            'file_type': self.file_type,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }