from unittest import TestCase

from app import app
from models import db, User, default_url, Post, Tag, PostTag
from datetime import datetime

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test_db'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class BloglyTestCase(TestCase):
    """Tests for views of Users, Posts, Tags"""

    def setUp(self):
        """Add Sample user/post/tags"""
        PostTag.query.delete()
        Post.query.delete()
        Tag.query.delete()
        User.query.delete()

        user = User(first_name="FirstName", last_name="LastName")

        db.session.add(user)
        db.session.commit()

        post = Post(title="TestTitle", content="TestContent", user_id=user.id)
        tag = Tag(name="TestTag")
        post.tags.append(tag)

        db.session.add(post)
        db.session.add(tag)
        db.session.commit()

        self.user_id = user.id
        self.post_id = post.id
        self.tag_id = tag.id
        self.user = user
        self.post = post
        self.tag = tag

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_list_users(self):
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.user.first_name, html)

    def test_user_details(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f"<h1>{self.user.first_name} {self.user.last_name}</h1>", html)

    def test_add_user(self):
        with app.test_client() as client:
            first_name = "John"
            last_name = "Wayne"
            new_user = {"first_name": first_name,
                        "last_name": last_name, "image_url": default_url}
            resp = client.post("/users/new", data=new_user,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            user_query = bool(User.query.filter_by(
                first_name=first_name).first())

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(user_query)
            self.assertIn(
                f"""<li><a href="/users/{self.user_id+1}">{first_name} {last_name}</a></li>""", html)

    def test_edit_user(self):
        with app.test_client() as client:
            first_name = "Tarzan"
            last_name = "KingOfApes"
            edit_user = {"first_name": first_name,
                         "last_name": last_name, "image_url": default_url}
            resp = client.post(f"/users/{self.user_id}/edit", data=edit_user,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            test_user = User.query.get(self.user_id)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(test_user.first_name, first_name)
            self.assertEqual(test_user.last_name, last_name)
            self.assertIn(
                f"""<li><a href="/users/{self.user_id}">{first_name} {last_name}</a></li>""", html)

    def test_delete_user(self):
        with app.test_client() as client:
            resp = client.post(f"/users/{self.user_id}/delete",
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            user_query = bool(User.query.filter_by(
                first_name=self.user.first_name).first())

            self.assertEqual(resp.status_code, 200)
            self.assertFalse(user_query)
            self.assertNotIn(f"{self.user.first_name}", html)

    def test_view_post(self):
        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"<h1>{self.post.title}</h1>", html)

    def test_add_post(self):
        with app.test_client() as client:
            post_title = "TestTitle2"
            new_post = {"title": post_title,
                        "content": "TestContent2", "user_id": self.user_id, "tags": self.tag_id}
            resp = client.post(f"/users/{self.user_id}/posts/new", data=new_post,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            post_query = bool(Post.query.filter_by(
                title=post_title).first())

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(post_query)
            self.assertIn(f"<li>{post_title}</li>", html)

    def test_edit_post(self):
        with app.test_client() as client:
            post_title = "Blah Blah"
            edit_post = {"title": post_title,
                         "content": "Blah Blah Blah"}
            resp = client.post(f"/posts/{self.post_id}/edit", data=edit_post,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            test_post = Post.query.get(self.post_id)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(test_post.title, post_title)
            self.assertIn(f"<h1>{post_title}</h1>", html)

    def test_delete_post(self):
        with app.test_client() as client:
            resp = client.post(
                f"/posts/{self.post_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            post_query = bool(Post.query.filter_by(
                title=self.post.title).first())

            self.assertEqual(resp.status_code, 200)
            self.assertFalse(post_query)
            self.assertNotIn(f"<h1>{self.post.title}</h1>", html)

    def test_list_tags(self):
        with app.test_client() as client:
            resp = client.get(f"/tags")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Tags</h1>', html)
            self.assertIn(self.tag.name, html)

    def test_add_tag(self):
        with app.test_client() as client:
            tag_name = "testtag22"
            new_tag = {"name": tag_name}
            resp = client.post(f"/tags/new", data=new_tag,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            tag_query = bool(Tag.query.filter_by(name=tag_name).first())

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(tag_query)
            self.assertIn(
                f"""<li><a href="/tags/{self.tag_id+1}">{tag_name}</a></li>""", html)

    def test_edit_tag(self):
        with app.test_client() as client:
            tag_name = "testtag22"
            edit_tag = {"name": tag_name}
            resp = client.post(f"/tags/{self.tag_id}/edit", data=edit_tag,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            test_tag = Tag.query.get(self.tag_id)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(test_tag.name, tag_name)
            self.assertIn(
                f"""<h1>{tag_name}</h1>""", html)

    def test_delete_tag(self):
        with app.test_client() as client:
            resp = client.post(
                f"/tags/{self.tag_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            tag_query = bool(Tag.query.filter_by(
                name=self.tag.name).first())

            self.assertEqual(resp.status_code, 200)
            self.assertFalse(tag_query)
            self.assertNotIn(f"<h1>{self.tag.name}</h1>", html)
