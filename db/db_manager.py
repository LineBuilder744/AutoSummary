from .models import Session, Summary

class DatabaseManager:
    def __init__(self):
        self.session = Session()
    
    def close(self):
        """Close the database session"""
        self.session.close()
    
    def add_summary(self, title:str, content: str, subject:str=None, author:str=None):
        """Add a new summary to the database"""
        summary = Summary(title=title, content=content, subject=subject.lower() if subject else None, author=author)
        self.session.add(summary)
        self.session.commit()
        return summary.id
    
    def get_summary(self, summary_id):
        """Get a summary by its ID"""
        return self.session.query(Summary).filter(Summary.id == summary_id).first()
    
    def get_all_summaries(self):
        """Get all summaries"""
        return self.session.query(Summary).all()
    
    def get_summaries_by_subject(self, subject):
        """Get all summaries for a specific subject"""
        return self.session.query(Summary).filter(Summary.subject == subject).all()
    
    def get_summaries_by_title(self, title):
        """Get all summaries that match the given title"""
        return self.session.query(Summary).filter(Summary.title == title).all()
    
    def get_summaries_by_author(self, author):
        """Get all summaries by a specific author"""
        return self.session.query(Summary).filter(Summary.author == author).all()
    
    def update_summary(self, summary_id, title=None, content=None, subject=None, author=None):
        """Update an existing summary"""
        summary = self.get_summary(summary_id)
        if not summary:
            return False
        
        if title:
            summary.title = title
        if content:
            summary.content = content
        if subject is not None:  # Allow setting subject to None
            summary.subject = subject
        if author is not None:  # Allow setting author to None
            summary.author = author
            
        self.session.commit()
        return True
    
    def delete_summary(self, summary_id):
        """Delete a summary by its ID"""
        summary = self.get_summary(summary_id)
        if not summary:
            return False
        
        self.session.delete(summary)
        self.session.commit()
        return True