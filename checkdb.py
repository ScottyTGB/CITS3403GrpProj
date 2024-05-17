from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from initdb import User, Tutor, Request

engine = create_engine('sqlite:///site.db')
Session = sessionmaker(bind=engine)
session = Session()

# insert for testing
def insert_test_data():
    user1 = User(userEmail='user3@example.com', userPassword='3')
    user2 = User(userEmail='user4@example.com', userPassword='4')
    
    tutor1 = Tutor(userID=3)
    tutor2 = Tutor(userID=4)
    
    request1 = Request(userID=3, tutorID=3, unit='Math')
    request2 = Request(userID=4, tutorID=4, unit='Science')
    
    session.add_all([user1, user2, tutor1, tutor2, request1, request2])
    session.commit()


def print_user_data():
    users = session.query(User).all()
    for user in users:
        print(f'User ID: {user.userID}, Email: {user.userEmail}, Password: {user.userPassword}')


def print_request_data():
    requests = session.query(Request).all()
    for req in requests:
        print(f'Request ID: {req.requestID}, User ID: {req.userID}, Tutor ID: {req.tutorID}, Unit: {req.unit}')


def print_tutor_data():
    tutors = session.query(Tutor).all()
    for tutor in tutors:
        print(f'Tutor ID: {tutor.tutorID}, User ID: {tutor.userID}')

if __name__ == "__main__":
    #insert_test_data() 
    print("User Data:")
    print_user_data()
    print("\nRequest Data:")
    print_request_data()
    print("\nTutor Data:")
    print_tutor_data()
