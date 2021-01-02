from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.urls import resolve
from django.test import TestCase
from .views import signup
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.core import mail

class SignUpTests(TestCase):
	def setUp(self):
		url = reverse('signup')
		self.response = self.client.get(url)

	def test_signup_status_code(self):
		url = reverse('signup')
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)

	def test_signup_url_resolves_signup_view(self):
		view = resolve('/signup/')
		self.assertEquals(view.func, signup)

	def test_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	def test_contains_form(self):
		form = self.response.context.get('form')
		self.assertIsInstance(form, SignUpForm)


	def test_form_inputs(self):
		self.assertContains(self.response, '<input', 5)
		self.assertContains(self.response, 'type="text"', 1)
		self.assertContains(self.response, 'type="email"', 1)
		self.assertContains(self.response, 'type="password"', 2)



class SuccessfulSignUpTests(TestCase):
	def setUp(self):
		url = reverse('signup')
		data = {
			'username': 'john',
			'email': 'john@doe.com',
			'password1': 'abcdef123456',
			'password2': 'abcdef123456'
		}
		self.response = self.client.post(url, data)
		self.home_url = reverse('home')

	def test_redirection(self):
		'''
		A valid form submission should redirect the user to the home page
		'''
		self.assertRedirects(self.response, self.home_url)

	def test_user_creation(self):
		self.assertTrue(User.objects.exists())

	def test_user_authentication(self):
		response = self.client.get(self.home_url)
		user = response.context.get('user')
		self.assertTrue(user.is_authenticated)



class InvalidSignUpTests(TestCase):
	def setUp(self):
		url = reverse('signup')
		self.response = self.client.post(url, {})  # submit an empty dictionary

	def test_signup_status_code(self):
		'''
		An invalid form submission should return to the same page	
		'''
		self.assertEquals(self.response.status_code, 200)

	def test_form_errors(self):
		form = self.response.context.get('form')
		self.assertTrue(form.errors)

	def test_dont_create_user(self):
		self.assertFalse(User.objects.exists())

# password reset test cases

class PasswordResetTests(TestCase):
	def setUp(self):
		url = reverse('password_reset')
		self.response = self.client.get(url)

	def test_status_code(self):
		self.assertEquals(self.response.status_code, 200)

	def test_view_function(self):
		view = resolve('/reset/')
		self.assertEquals(view.func.view_class, auth_views.PasswordResetView)

	def test_csrf(self):
		self.assertContains(self.response, 'csrfmiddlewaretoken')

	def test_contains_form(self):
		form = self.response.context.get('form')
		self.assertIsInstance(form, PasswordResetForm)

	def test_form_inputs(self):
		'''
		The view must contain two inputs: csrf and email
		'''
		self.assertContains(self.response, '<input', 2)
		self.assertContains(self.response, 'type="email"', 1)


class SuccessfulPasswordResetTests(TestCase):
	def setUp(self):
		email = 'john@doe.com'
		User.objects.create_user(username='john', email=email, password='123abcdef')
		url = reverse('password_reset')
		self.response = self.client.post(url, {'email': email})

	def test_redirection(self):
		'''
		A valid form submission should redirect the user to `password_reset_done` view
		'''
		url = reverse('password_reset_done')
		self.assertRedirects(self.response, url)

	def test_send_password_reset_email(self):
		self.assertEqual(1, len(mail.outbox))


class InvalidPasswordResetTests(TestCase):
	def setUp(self):
		url = reverse('password_reset')
		self.response = self.client.post(url, {'email': 'donotexist@email.com'})

	def test_redirection(self):
		'''
		Even invalid emails in the database should
		redirect the user to `password_reset_done` view
		'''
		url = reverse('password_reset_done')
		self.assertRedirects(self.response, url)

	def test_no_reset_email_sent(self):
		self.assertEqual(0, len(mail.outbox))
# Create your tests here.
