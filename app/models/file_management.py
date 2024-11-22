from app import db


class FileManagement(db.Model):
    __tablename__ = 'file_management'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    filepath = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(255), nullable=False) # cls, detect
    image_path = db.Column(db.Text, nullable=True)
    model_name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


    def __repr__(self):
        return f'<FileManagement {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'filename': self.filename,
            'filepath': self.filepath,
            'file_type': self.file_type,
            'image_path': self.image_path,
            'model_name': self.model_name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }