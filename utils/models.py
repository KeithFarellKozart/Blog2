#from email.mime import image
#from os import name
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(120), nullable=True)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")

    def __init__(self, username=None, email=None, password=None):
        self.username = username
        self.email = email
        self.password = password
        
    def __repr__(self):
        return f'<User {self.username!r}>'

    
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title= Column(String(120), nullable=False)
    text = Column(Text())
    author = Column(Integer, ForeignKey(User.id), nullable=True)
    user = relationship("User", back_populates="posts")
    image = Column(String(120), nullable=True)
    comments = relationship("Comment", back_populates="posts")


    def __init__(self, title=None, text=None, author=None, image=None) -> None:
        self.title = title
        self.text = text
        self.author = author
        self.image = image
    
    def __repr__(self):
        return f"<Post {self.title!r}>"  
    

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    text = Column(Text())
    author = Column(Integer, ForeignKey(User.id), nullable=True)
    user = relationship("User", back_populates="comments")
    posts = relationship("Post", back_populates="comments")
    image = Column(String(120), nullable=True)
    post = Column(Integer, ForeignKey(Post.id), nullable=True)

    def __init__(self, title=None, text=None, author=None, post=None, image=None) -> None:
        self.title = title
        self.text = text
        self.author = author
        self.post = post
        self.image = image


    def __repr__(self):
        return f"<Comment {self.title!r}>"  