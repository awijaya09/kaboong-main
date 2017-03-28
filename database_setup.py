from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'

  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  email = Column(String(250), nullable=False)
  password = Column(String(100), nullable=False)
  picture = Column(String(250))
  member_since = Column(String(250), nullable=False)

class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    date_created = Column(String(250))
    d_name = Column(String(250), nullable=False)
    d_age = Column(Integer)
    d_tod = Column(String(250))
    d_resting_at = Column(String(250))
    d_burried_at = Column(String(250))
    d_burried_date = Column(String(250))
    picture = Column(String(250))
    obituary = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class Family(Base):
    __tablename__ = 'family'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship(Post)
    name = Column(String(250), nullable=False)
    relation = Column(String(250), nullable=False)

class Ads(Base):
    __tablename__ = 'ads'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship(Post)
    category = Column(String(250))
    picture = Column(String(250))

class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship(Post)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    date_posted = Column(String(250), nullable=False)

engine = create_engine('mysql://obitsy:kiasu123@localhost/obitsy_db')

Base.metadata.create_all(engine)