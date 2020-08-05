from datetime import datetime, timedelta
import unittest

from app import db, create_app
from app.models import User, Post
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='bob')
        u.set_password('bab')
        self.assertFalse(u.check_password('beeb'))
        self.assertTrue(u.check_password('bab'))

    def test_avatar(self):
        u = User(username='jim', email='slim@jim.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         '8f9043c38e535a0eb1240a5435b6cc2a'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(username='jim', email='slim@jim.com')
        u2 = User(username='bob', email='bob@jim.com')
        db.session.add(u1)
        db.session.add(u2)
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'bob')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'jim')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create user list
        u1 = User(username='jim', email='slim@jim.com')
        u2 = User(username='bob', email='bob@jim.com')
        u3 = User(username='joe', email='joe@jim.com')
        u4 = User(username='howard', email='howard@jim.com')
        users = [u1, u2, u3, u4]
        db.session.add_all(users)

        # create posts for each user
        now = datetime.utcnow()
        p = [Post(body=f'post from {u.username}',
                  author=u, timestamp=now + timedelta(seconds=i))
             for i, u in enumerate(users)]
        db.session.add_all(p)
        db.session.commit()

        # setup follower relationships
        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        # check the followed posts of each user
        f = [u.followed_posts().all() for u in users]
        self.assertEqual(f[0], [p[3], p[1], p[0]])
        self.assertEqual(f[1], p[1:3][::-1])
        self.assertEqual(f[2], p[2:][::-1])
        self.assertEqual(f[3], p[3:4])

if __name__ == '__main__':
    unittest.main(verbosity=2)
