from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Create the base directory if it doesn't exist
os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

# Create the database engine
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'summaries.db')
engine = create_engine(f'sqlite:///{db_path}')

# Create a base class for our models
Base = declarative_base()

# Define the Summary model
class Summary(Base):
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    author = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<Summary(id={self.id}, title='{self.title}', subject='{self.subject}', author='{self.author}')>"

# Create all tables
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)