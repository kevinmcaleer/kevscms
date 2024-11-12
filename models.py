from fasthtml import *
from fasthtml.common import *
from dataclasses import dataclass

@dataclass
class User:
    id: int # primary key
    firstname: str # 'First Name']
    lastname: str 
    email: str
    username: str
    user_type: str  # 'admin, user']
    is_active: bool
    date_created: str # need to change this to a date type
    is_admin: bool
    password: str

    def __ft__(self):
        return Li("User", self.id, self.username, self.email, self.password, self.is_active, self.is_admin)

@dataclass
class Post:
    id: int
    title: str
    user_id: int# foreign key
    date_created : str
    date_last_updated: str

    def __ft__(self):
        return Li("Post", self.title, self.date_created, self.date_last_updated) 
    
@dataclass
class Post_text:
    id: int
    post_id: int # foreign key
    content: str
    date_created: str
    date_last_updated: str
    purpose: str # 'content, summary, excerpt']

@dataclass
class Media:
    id: int
    post_id: int # foreign key
    filename: str
    type: str
    date_created: str
    purpose: str # 'thumbnail, image, video']

@dataclass
class Comment:
    id: int
    post_id: int # foreign key
    comment: str
    user_id: int # foreign key
    date_created: str

@dataclass
class Like:
    id: int
    post_id: int # foreign key
    user_id: int # foreign key
    date_created: str