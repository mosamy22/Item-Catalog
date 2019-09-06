from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dbconfig import Country, Base, Club, User

engine = create_engine('sqlite:///itemcatalog.db')
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


# Create dummy user
User1 = User(name="Mohamed Samy", email="mohamedsamyhasan486@gmail.com")
session.add(User1)
session.commit()

country1 = Country(user_id = 1,name = "Egypt")

session.add(country1)
session.commit()

club1 = Club(user_id = 1,title = "Alahly", description = "The biggest club in Africa and it had been opened since 1907 ",country_name = "Egypt",country = country1)

session.add(club1)
session.commit()

club2 = Club(user_id = 1,title = "AlZamalek", description = "Unknown Club",country_name = "Egypt",country = country1)

session.add(club2)
session.commit()



country2 = Country(user_id = 1,name = "Spain")

session.add(country2)
session.commit()

club3 = Club(user_id = 1,title = "Real Madrid", description = "Royal Club ",country_name = "Spain",country = country2)

session.add(club3)
session.commit()

club4 = Club(user_id = 1,title = "Barcelona", description = "Messi",country_name = "Spain",country = country2)

session.add(club4)
session.commit()

country3 = Country(user_id = 1,name = "England")

session.add(country3)
session.commit()

club5 = Club(user_id = 1,title = "Arsenal", description = "Gunners ",country_name = "England",country = country3)

session.add(club5)
session.commit()

club6 = Club(user_id = 1,title = "Manchester United", description = "Red devils",country_name = "England",country = country3)

session.add(club6)
session.commit()


country4 = Country(user_id = 1,name = "Italy")

session.add(country4)
session.commit()

club7 = Club(user_id = 1,title = "Juventus", description = "The old woman team ",country_name = "Italy",country = country4)

session.add(club7)
session.commit()

club8 = Club(user_id = 1,title = "AC Milan", description = "Chineses",country_name = "Italy",country = country4)

session.add(club8)
session.commit()


country5 = Country(user_id = 1,name = "Germany")

session.add(country5)
session.commit()

club9 = Club(user_id = 1,title = "Bayern Munchine", description = "The Great Team",country_name = "Germany",country = country5)

session.add(club9)
session.commit()

club10 = Club(user_id = 1,title = "Brusia Dortmund", description = "The yelow black heroes",country_name = "Germany",country = country5)

session.add(club10)
session.commit()

country6 = Country(user_id = 1,name = "France")

session.add(country6)
session.commit()

club11 = Club(user_id = 1,title = "Baris SanitGerman", description = "The Capital team ",country_name = "France",country = country6)

session.add(club11)
session.commit()

club12 = Club(user_id = 1,title= "Monaco", description = "second team in table",country_name = "France",country = country6)

session.add(club12)
session.commit()


print "added items!"
