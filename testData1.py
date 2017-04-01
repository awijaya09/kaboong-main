from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Post, Comment, Family, Ads, City
from logic import hash_str
engine = create_engine('mysql://obitsy:Kiasu123@localhost/obitsy_db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1 = User(name="Andree Wijaya", email="andree@twiscode.com", password=hash_str("kiasu123"), picture="http://vignette3.wikia.nocookie.net/gameofthrones/images/4/4c/JoffreyBaratheon-Profile.PNG/revision/latest?cb=20160626094917", member_since="25 March 2017")
session.add(user1)
session.commit()

print "User 'Andree Wijaya' created"

user2 = User(name="Ding Dong Dong", email="ding@twiscode.com", password=hash_str("ding123"), picture="http://vignette2.wikia.nocookie.net/gameofthrones/images/b/bb/TywinLannister-Profile.PNG/revision/latest?cb=20160626095349", member_since="28 March 2017")
session.add(user2)
session.commit()

print "User 'Ding Dong Dong' created"

city1 = City(name="surabaya")
session.add(city1)
session.commit()

print "City 'Surabaya' created"

city2 = City(name="jakarta")
session.add(city2)
session.commit()

print "City 'Jakarta' created"

post1 = Post(date_created="26 March 2017", d_name="John Doe", d_age=43, d_tod="25 March 2017", d_resting_at="Adijasa VIP Ruang 6",
             d_burried_at="Lawang", d_burried_date="31 March 2017", picture="http://vignette3.wikia.nocookie.net/gameofthrones/images/4/4c/JoffreyBaratheon-Profile.PNG/revision/latest?cb=20160626094917",
             obituary="He is a tall and handsome man, too bad he owes people lots of money. He got killed trying to escape!",
             user=user1, city=city1)
session.add(post1)
session.commit()
print "Post 1, John Doe's Death, created!"

post2 = Post(date_created="23 March 2017", d_name="Budi Santoso", d_age=56, d_tod="22 March 2017", d_resting_at="Jakarta",
             d_burried_at="Bandung", d_burried_date="24 March 2017", picture="http://vignette2.wikia.nocookie.net/gameofthrones/images/b/bb/TywinLannister-Profile.PNG/revision/latest?cb=20160626095349",
             obituary="Budi is nice, Budi is kind. He helped many people. Be like Budi",
             user=user2, city=city2)
session.add(post2)
session.commit()
print "Post 2, Budi's Death, created!"

family1 = Family(post=post1, name="Jane Doe", relation="Sister")
session.add(family1)
session.commit()
print "Family 1, Jane Doe, created!"

family2 = Family(post=post1, name="Jasper Doe", relation="Father")
session.add(family2)
session.commit()
print "Family 2, Jasper Doe, created!"

family3 = Family(post=post2, name="Hari Santoso", relation="Brother")
session.add(family3)
session.commit()
print "Family 3, Hari Santoso, created!"

comment1 = Comment(post=post1, user=user2, content="Sorry to hear about your lost Jane!I'm happy for you!", date_posted="26 March 2017")
session.add(comment1)
session.commit()
print "Comment 1 created!"