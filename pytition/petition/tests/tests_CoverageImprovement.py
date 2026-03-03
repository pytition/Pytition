"""
Test suite for improving code coverage in Pytition project.
This module demonstrates usage of:
- Mocks: Simulating external dependencies (email sending, HTTP requests)
- Stubs: Providing predefined responses to method calls
- Fakes: Simplified implementations of complex objects

Author: Generated for coverage improvement
"""

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from unittest.mock import Mock, patch, MagicMock, call
from unittest import skip

from petition.models import (
    Organization, Petition, PytitionUser, Signature, 
    PetitionTemplate, Permission, SlugModel, ModerationReason
)
from petition.helpers import (
    sanitize_html, get_client_ip, get_session_user, check_user_in_orga,
    petition_from_id, check_petition_is_accessible, send_confirmation_email,
    send_welcome_mail, subscribe_to_newsletter, get_update_form,
    settings_context_processor, footer_content_processor, petition_detail_meta,
    remove_user_moderated
)
from petition.forms import (
    SignatureForm, PetitionCreationStep1, NewsletterForm, 
    OrgCreationForm, DeleteAccountForm, UpdateInfoForm
)
from petition.widgets import SwitchWidget, SwitchField
from petition.templatetags.petition_extras import addstr, getitem, bootstrap


# ============================================================================
# HELPER FUNCTION TESTS - Using Mocks and Stubs
# ============================================================================

class SanitizeHtmlTest(TestCase):
    """Tests for sanitize_html helper function"""
    
    def test_sanitize_html_removes_javascript(self):
        """Test that JavaScript is removed from HTML"""
        unsafe_html = '<div onclick="alert(1)">Hello<script>alert("xss")</script></div>'
        result = sanitize_html(unsafe_html)
        self.assertNotIn('script', result.lower())
        self.assertNotIn('onclick', result.lower())
    
    def test_sanitize_html_empty_input(self):
        """Test sanitization with empty string"""
        result = sanitize_html('')
        self.assertEqual(result, '')
    
    def test_sanitize_html_invalid_html(self):
        """Test sanitization with invalid HTML - should return empty string"""
        # Testing line 29-30 in helpers.py (exception handling)
        result = sanitize_html(None)
        self.assertEqual(result, '')


class GetClientIpTest(TestCase):
    """Tests for get_client_ip helper function using Stubs"""
    
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test IP extraction from X-Forwarded-For header (STUB pattern)"""
        # Create a stub request object
        request = Mock()
        request.META = {'HTTP_X_FORWARDED_FOR': '192.168.1.1, 10.0.0.1'}
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_without_proxy(self):
        """Test IP extraction from REMOTE_ADDR (STUB pattern)"""
        request = Mock()
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        
        ip = get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')
    
    def test_get_client_ip_no_headers(self):
        """Test IP extraction when no headers present"""
        request = Mock()
        request.META = {}
        
        ip = get_client_ip(request)
        self.assertIsNone(ip)


class GetSessionUserTest(TestCase):
    """Tests for get_session_user helper using Mocks"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('testuser', password='testpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
    
    def test_get_session_user_valid(self):
        """Test getting session user with valid request"""
        request = Mock()
        request.user = self.user
        
        result = get_session_user(request)
        self.assertEqual(result, self.pytition_user)
    
    def test_get_session_user_not_found(self):
        """Test get_session_user raises Http404 for non-existent user"""
        from django.http import Http404
        
        request = Mock()
        request.user = Mock()
        request.user.username = 'nonexistent_user_xyz'
        
        with self.assertRaises(Http404):
            get_session_user(request)


class CheckUserInOrgaTest(TestCase):
    """Tests for check_user_in_orga helper - Testing line 51-53"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('orguser', password='orgpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.org = Organization.objects.create(name='TestOrg')
    
    def test_check_user_not_in_org(self):
        """Test that HttpResponseForbidden is returned when user is not in org"""
        result = check_user_in_orga(self.pytition_user, self.org)
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 403)
    
    def test_check_user_in_org(self):
        """Test that None is returned when user is in org"""
        self.org.members.add(self.pytition_user)
        result = check_user_in_orga(self.pytition_user, self.org)
        self.assertIsNone(result)


class PetitionFromIdTest(TestCase):
    """Tests for petition_from_id helper"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('petuser', password='petpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.petition = Petition.objects.create(title='Test Petition', user=self.pytition_user)
    
    def test_petition_from_id_valid(self):
        """Test getting petition with valid ID"""
        result = petition_from_id(self.petition.id)
        self.assertEqual(result, self.petition)
    
    def test_petition_from_id_not_found(self):
        """Test Http404 raised for invalid petition ID - Testing line 70-71"""
        from django.http import Http404
        
        with self.assertRaises(Http404):
            petition_from_id(99999)


class CheckPetitionIsAccessibleTest(TestCase):
    """Tests for check_petition_is_accessible helper - Testing lines 78-90"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('accessuser', password='accesspass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.petition = Petition.objects.create(title='Access Test', user=self.pytition_user)
        self.factory = RequestFactory()
    
    def test_published_petition_accessible(self):
        """Test that published petition is accessible"""
        self.petition.published = True
        self.petition.moderated = False
        self.petition.save()
        
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        result = check_petition_is_accessible(request, self.petition)
        self.assertTrue(result)
    
    def test_moderated_petition_raises_404(self):
        """Test that moderated petition raises Http404 - Line 88-89"""
        from django.http import Http404
        
        self.petition.published = True
        self.petition.moderated = True
        self.petition.save()
        
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        with self.assertRaises(Http404):
            check_petition_is_accessible(request, self.petition)
    
    def test_unpublished_petition_raises_404(self):
        """Test that unpublished petition raises Http404 - Line 90"""
        from django.http import Http404
        
        self.petition.published = False
        self.petition.moderated = False
        self.petition.save()
        
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        with self.assertRaises(Http404):
            check_petition_is_accessible(request, self.petition)


# ============================================================================
# EMAIL SENDING TESTS - Using Mocks
# ============================================================================

class SendConfirmationEmailTest(TestCase):
    """Tests for send_confirmation_email using Mock for email backend"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('emailuser', password='emailpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.petition = Petition.objects.create(
            title='Email Test',
            user=self.pytition_user,
            confirmation_email_reply='reply@test.com'
        )
        self.signature = Signature.objects.create(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            petition=self.petition
        )
        self.factory = RequestFactory()
    
    @patch('petition.helpers.get_connection')
    @patch('petition.helpers.EmailMultiAlternatives')
    def test_send_confirmation_email_called(self, mock_email_class, mock_connection):
        """Test that email is sent correctly (MOCK pattern)"""
        # Create mock email instance
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email
        mock_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connection.return_value.__exit__ = Mock(return_value=False)
        
        request = self.factory.get('/')
        request.build_absolute_uri = Mock(return_value='http://test.com/confirm/1/hash')
        
        send_confirmation_email(request, self.signature)
        
        # Verify email was created and sent
        mock_email_class.assert_called_once()
        mock_email.attach_alternative.assert_called_once()
        mock_email.send.assert_called_once()


class SendWelcomeMailTest(TestCase):
    """Tests for send_welcome_mail using Mock"""
    
    @patch('petition.helpers.get_connection')
    @patch('petition.helpers.EmailMultiAlternatives')
    def test_send_welcome_mail(self, mock_email_class, mock_connection):
        """Test welcome mail sending (MOCK pattern) - Testing lines 123-130"""
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email
        mock_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connection.return_value.__exit__ = Mock(return_value=False)
        
        user_infos = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        send_welcome_mail(user_infos)
        
        mock_email_class.assert_called_once()
        mock_email.send.assert_called_once()


class SubscribeToNewsletterTest(TestCase):
    """Tests for subscribe_to_newsletter using Mocks - Testing lines 129-152"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('newsuser', password='newspass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
    
    @patch('petition.helpers.requests.post')
    def test_subscribe_via_post(self, mock_post):
        """Test newsletter subscription via POST method (MOCK pattern)"""
        petition = Petition.objects.create(
            title='POST Newsletter Test',
            user=self.pytition_user,
            newsletter_subscribe_method='POST',
            newsletter_subscribe_http_url='http://newsletter.example.com/subscribe',
            newsletter_subscribe_http_mailfield='email',
            newsletter_subscribe_http_data='{"list": "main"}'
        )
        
        subscribe_to_newsletter(petition, 'subscriber@test.com')
        
        mock_post.assert_called_once()
    
    @patch('petition.helpers.requests.get')
    def test_subscribe_via_get(self, mock_get):
        """Test newsletter subscription via GET method (MOCK pattern)"""
        petition = Petition.objects.create(
            title='GET Newsletter Test',
            user=self.pytition_user,
            newsletter_subscribe_method='GET',
            newsletter_subscribe_http_url='http://newsletter.example.com/subscribe',
            newsletter_subscribe_http_mailfield='email'
        )
        
        subscribe_to_newsletter(petition, 'subscriber@test.com')
        
        mock_get.assert_called_once()
    
    @patch('petition.helpers.get_connection')
    @patch('petition.helpers.EmailMessage')
    def test_subscribe_via_mail(self, mock_email, mock_connection):
        """Test newsletter subscription via MAIL method (MOCK pattern)"""
        mock_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_connection.return_value.__exit__ = Mock(return_value=False)
        mock_email_instance = MagicMock()
        mock_email.return_value = mock_email_instance
        
        petition = Petition.objects.create(
            title='MAIL Newsletter Test',
            user=self.pytition_user,
            newsletter_subscribe_method='MAIL',
            newsletter_subscribe_mail_subject='Subscribe {}',
            newsletter_subscribe_mail_from='admin@list.com',
            newsletter_subscribe_mail_to='list@list.com',
            newsletter_subscribe_mail_smtp_host='localhost',
            newsletter_subscribe_mail_smtp_port=25
        )
        
        subscribe_to_newsletter(petition, 'subscriber@test.com')
        
        mock_email.assert_called_once()
        mock_email_instance.send.assert_called_once()
    
    def test_subscribe_empty_url(self):
        """Test that subscription with empty URL does nothing"""
        petition = Petition.objects.create(
            title='Empty URL Test',
            user=self.pytition_user,
            newsletter_subscribe_method='POST',
            newsletter_subscribe_http_url=''
        )
        
        # Should not raise any exception
        subscribe_to_newsletter(petition, 'test@test.com')


# ============================================================================
# WIDGET TESTS - Testing widgets.py coverage
# ============================================================================

class SwitchWidgetTest(TestCase):
    """Tests for SwitchWidget - Testing lines 8, 12, 21 in widgets.py"""
    
    def test_get_context_with_existing_class(self):
        """Test get_context when attrs already has class - Line 12"""
        widget = SwitchWidget()
        widget.label = 'Test Label'
        
        context = widget.get_context('test_field', True, {'class': 'existing-class'})
        
        self.assertIn('custom-control-input', context['widget']['attrs']['class'])
        self.assertIn('existing-class', context['widget']['attrs']['class'])
    
    def test_get_context_without_attrs(self):
        """Test get_context when attrs is None - Line 8"""
        widget = SwitchWidget()
        widget.label = 'Test Label'
        
        context = widget.get_context('test_field', True, None)
        
        self.assertEqual(context['widget']['attrs']['class'], 'custom-control-input')
    
    def test_init_with_label(self):
        """Test widget initialization with label - Line 21"""
        widget = SwitchWidget(label='Custom Label')
        # Should not raise an exception


class SwitchFieldTest(TestCase):
    """Tests for SwitchField - Testing line 37 in widgets.py"""
    
    def test_label_tag_returns_empty(self):
        """Test that label_tag returns empty string - Line 37"""
        field = SwitchField(label='Test')
        result = field.label_tag()
        self.assertEqual(result, '')


# ============================================================================
# TEMPLATETAG TESTS - Testing petition_extras.py coverage
# ============================================================================

class TemplateTagsTest(TestCase):
    """Tests for template tags - Testing lines 12, 16, 25, 27"""
    
    def test_addstr_concatenates_strings(self):
        """Test addstr filter - Line 12"""
        result = addstr('Hello', ' World')
        self.assertEqual(result, 'Hello World')
    
    def test_addstr_with_numbers(self):
        """Test addstr with numbers"""
        result = addstr(10, 20)
        self.assertEqual(result, '1020')
    
    def test_getitem_returns_value(self):
        """Test getitem filter - Line 16"""
        array = {'key': 'value'}
        result = getitem(array, 'key')
        self.assertEqual(result, 'value')
    
    def test_bootstrap_with_textarea(self):
        """Test bootstrap filter with textarea widget - Line 25"""
        from django import forms
        
        class TestForm(forms.Form):
            text = forms.CharField(widget=forms.Textarea)
        
        form = TestForm()
        field = form['text']
        result = bootstrap(field)
        
        self.assertIn('form-control', str(result))
    
    def test_bootstrap_with_checkbox(self):
        """Test bootstrap filter with checkbox widget - Line 27"""
        from django import forms
        
        class TestForm(forms.Form):
            agree = forms.BooleanField(widget=forms.CheckboxInput)
        
        form = TestForm()
        field = form['agree']
        result = bootstrap(field)
        
        self.assertIn('form-check-input', str(result))
    
    def test_bootstrap_with_file_input(self):
        """Test bootstrap filter with file input"""
        from django import forms
        
        class TestForm(forms.Form):
            file = forms.FileField(widget=forms.FileInput)
        
        form = TestForm()
        field = form['file']
        result = bootstrap(field)
        
        self.assertIn('form-control-file', str(result))
    
    def test_bootstrap_with_unsupported_widget(self):
        """Test bootstrap filter returns field unchanged for unsupported widget"""
        from django import forms
        
        class CustomWidget(forms.Widget):
            pass
        
        class TestForm(forms.Form):
            custom = forms.CharField(widget=CustomWidget)
        
        form = TestForm()
        field = form['custom']
        result = bootstrap(field)
        
        # Should return field unchanged
        self.assertEqual(result, field)


# ============================================================================
# FORM VALIDATION TESTS - Using Fakes
# ============================================================================

class NewsletterFormTest(TestCase):
    """Tests for NewsletterForm validation - Testing forms.py coverage"""
    
    def test_newsletter_form_both_tls_and_starttls(self):
        """Test validation error when both TLS and STARTTLS are selected"""
        form_data = {
            'has_newsletter': True,
            'newsletter_text': 'Subscribe',
            'newsletter_subscribe_method': 'MAIL',
            'newsletter_subscribe_mail_smtp_tls': True,
            'newsletter_subscribe_mail_smtp_starttls': True,
            'newsletter_subscribe_mail_smtp_port': 25
        }
        form = NewsletterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('newsletter_subscribe_mail_smtp_tls', form.errors)
    
    def test_newsletter_form_invalid_port(self):
        """Test validation error for invalid SMTP port"""
        form_data = {
            'has_newsletter': True,
            'newsletter_subscribe_mail_smtp_port': 70000  # Invalid port
        }
        form = NewsletterForm(data=form_data)
        self.assertFalse(form.is_valid())


class OrgCreationFormTest(TestCase):
    """Tests for OrgCreationForm validation"""
    
    def test_invalid_org_name_dots(self):
        """Test that '.' and '..' are invalid org names"""
        form = OrgCreationForm(data={'name': '..'})
        self.assertFalse(form.is_valid())
        
        form = OrgCreationForm(data={'name': '.'})
        self.assertFalse(form.is_valid())
    
    def test_valid_org_name(self):
        """Test valid organization name"""
        form = OrgCreationForm(data={'name': 'Valid Org Name'})
        self.assertTrue(form.is_valid())


class DeleteAccountFormTest(TestCase):
    """Tests for DeleteAccountForm validation"""
    
    def test_incorrect_validation_code(self):
        """Test that incorrect validation code fails"""
        form = DeleteAccountForm(data={'validation': 'wrong code'})
        self.assertFalse(form.is_valid())
        self.assertIn('validation', form.errors)


class PetitionCreationStep1Test(TestCase):
    """Tests for PetitionCreationStep1 form - Testing lines 54-67"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('formuser', password='formpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.org = Organization.objects.create(name='FormOrg')
    
    def test_form_requires_org_or_user(self):
        """Test that form raises ValueError without org or user - Line 67"""
        with self.assertRaises(ValueError):
            PetitionCreationStep1(data={'title': 'Test'})
    
    def test_duplicate_title_for_user(self):
        """Test duplicate title validation for user petitions - Lines 54-66"""
        Petition.objects.create(title='Duplicate Title', user=self.pytition_user)
        
        form = PetitionCreationStep1(
            data={'title': 'Duplicate Title'},
            user_name=self.pytition_user.user.username
        )
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class SignatureFormTest(TestCase):
    """Tests for SignatureForm - Line 47"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('sigformuser', password='sigformpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
    
    def test_form_without_newsletter(self):
        """Test form when petition has no newsletter - Line 47"""
        petition = Petition.objects.create(
            title='No Newsletter',
            user=self.pytition_user,
            has_newsletter=False
        )
        
        form = SignatureForm(petition=petition)
        self.assertNotIn('subscribed_to_mailinglist', form.fields)
    
    def test_form_with_newsletter(self):
        """Test form when petition has newsletter"""
        petition = Petition.objects.create(
            title='With Newsletter',
            user=self.pytition_user,
            has_newsletter=True,
            newsletter_text='Subscribe to our list'
        )
        
        form = SignatureForm(petition=petition)
        self.assertIn('subscribed_to_mailinglist', form.fields)


# ============================================================================
# MODEL TESTS - Testing model edge cases
# ============================================================================

class PetitionModelTest(TestCase):
    """Tests for Petition model methods"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('modeluser', password='modelpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.org = Organization.objects.create(name='ModelOrg')
    
    def test_petition_owner_type_org(self):
        """Test owner_type property for org-owned petition"""
        petition = Petition.objects.create(title='Org Petition', org=self.org)
        self.assertEqual(petition.owner_type, 'org')
    
    def test_petition_owner_type_user(self):
        """Test owner_type property for user-owned petition"""
        petition = Petition.objects.create(title='User Petition', user=self.pytition_user)
        self.assertEqual(petition.owner_type, 'user')
    
    def test_petition_save_without_owner_raises(self):
        """Test that saving petition without owner raises exception"""
        petition = Petition(title='No Owner')
        with self.assertRaises(Exception):
            petition.save()
    
    def test_petition_save_with_both_owners_raises(self):
        """Test that saving petition with both owners raises exception"""
        petition = Petition(title='Both Owners', user=self.pytition_user, org=self.org)
        with self.assertRaises(Exception):
            petition.save()
    
    def test_transfer_petition_to_user(self):
        """Test transferring petition to user"""
        petition = Petition.objects.create(title='Transfer Test', org=self.org)
        petition.transfer_to(user=self.pytition_user)
        
        self.assertEqual(petition.user, self.pytition_user)
        self.assertIsNone(petition.org)
    
    def test_transfer_petition_invalid(self):
        """Test transfer with neither user nor org raises ValueError"""
        petition = Petition.objects.create(title='Transfer Invalid', org=self.org)
        
        with self.assertRaises(ValueError):
            petition.transfer_to()
    
    def test_transfer_petition_both_raises(self):
        """Test transfer with both user and org raises ValueError"""
        petition = Petition.objects.create(title='Transfer Both', org=self.org)
        
        with self.assertRaises(ValueError):
            petition.transfer_to(user=self.pytition_user, org=self.org)


class RemoveUserModeratedTest(TestCase):
    """Tests for remove_user_moderated helper function"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('moduser', password='modpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
    
    def test_remove_moderated_petitions(self):
        """Test that moderated petitions are removed from list"""
        petition1 = Petition.objects.create(title='Normal', user=self.pytition_user)
        petition2 = Petition.objects.create(title='Moderated', user=self.pytition_user, moderated=True)
        
        result = remove_user_moderated([petition1, petition2])
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], petition1)
    
    def test_remove_user_moderated_petitions(self):
        """Test that petitions from moderated users are removed"""
        self.pytition_user.moderated = True
        self.pytition_user.save()
        
        petition = Petition.objects.create(title='User Mod', user=self.pytition_user)
        
        result = remove_user_moderated([petition])
        self.assertEqual(len(result), 0)


# ============================================================================
# CONTEXT PROCESSOR TESTS
# ============================================================================

class ContextProcessorTest(TestCase):
    """Tests for context processors"""
    
    def test_settings_context_processor(self):
        """Test settings_context_processor returns settings"""
        from django.conf import settings as django_settings
        
        request = Mock()
        result = settings_context_processor(request)
        
        self.assertIn('settings', result)
        self.assertEqual(result['settings'], django_settings)
    
    @override_settings(FOOTER_TEMPLATE=None)
    def test_footer_content_processor_no_template(self):
        """Test footer_content_processor without template"""
        request = Mock()
        result = footer_content_processor(request)
        
        self.assertIn('footer_content', result)
        self.assertIsNone(result['footer_content'])


class PetitionDetailMetaTest(TestCase):
    """Tests for petition_detail_meta helper"""
    
    def test_petition_detail_meta(self):
        """Test petition_detail_meta returns correct URLs"""
        request = Mock()
        request.scheme = 'https'
        request.get_host.return_value = 'example.com'
        
        result = petition_detail_meta(request, 1)
        
        self.assertIn('site_url', result)
        self.assertIn('petition_url', result)
        self.assertEqual(result['site_url'], 'example.com')
        self.assertIn('https://example.com', result['petition_url'])


class GetUpdateFormTest(TestCase):
    """Tests for get_update_form helper"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            'updateuser', 
            password='updatepass',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
    
    def test_get_update_form_without_data(self):
        """Test get_update_form pre-populates with user data"""
        form = get_update_form(self.user)
        
        self.assertEqual(form.initial['first_name'], 'Test')
        self.assertEqual(form.initial['last_name'], 'User')
        self.assertEqual(form.initial['email'], 'test@example.com')
    
    def test_get_update_form_with_data(self):
        """Test get_update_form uses provided data"""
        custom_data = {
            'first_name': 'New',
            'last_name': 'Name',
            'email': 'new@example.com'
        }
        form = get_update_form(self.user, data=custom_data)
        
        self.assertEqual(form.data['first_name'], 'New')
