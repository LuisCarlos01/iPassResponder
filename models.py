"""
Automated Email Response System - Database Models

This module defines the database models for the email auto-responder system.
"""

from datetime import datetime
from app import db

class Rule(db.Model):
    """
    Rule model for storing email response rules.
    """
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), unique=True, nullable=False)
    response = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Rule {self.keyword}>"

class EmailLog(db.Model):
    """
    Email log model for tracking processed emails.
    """
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255))
    matched_rule = db.Column(db.String(100), nullable=True)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_sent = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<EmailLog {self.id} - {self.sender}>"