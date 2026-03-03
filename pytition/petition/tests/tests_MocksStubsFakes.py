
# Unit : Mocks, Stubs and Fakes

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseForbidden
from django.conf import settings
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from unittest import mock

from petition.models import (
    Organization, Petition, PytitionUser, Permission,
    Signature, PetitionTemplate, SlugModel
)
from petition.helpers import (
    sanitize_html, get_client_ip, get_session_user,
    check_user_in_orga, petition_from_id, check_petition_is_accessible,
    send_confirmation_email, send_welcome_mail, subscribe_to_newsletter,
    get_update_form, remove_user_moderated
)


# =============================================================================
# FAKE CLASSES - implementations for testing
# =============================================================================

class FakeRequest:
    
    def __init__(self, user=None, meta=None, get_params=None, scheme='http', host='testserver'):
        self.user = user or Mock()
        self.META = meta or {}
        self.GET = get_params or {}
        self.scheme = scheme
        self._host = host
    
    def get_host(self):
        return self._host
    
    def build_absolute_uri(self, path):
        return f"{self.scheme}://{self._host}{path}"


class FakePetition:
    
    def __init__(self, published=True, moderated=False, owner_type="user", owner=None):
        self.published = published
        self.moderated = moderated
        self._owner_type = owner_type
        self._owner = owner
        self.is_moderated = moderated
    
    @property
    def owner_type(self):
        return self._owner_type
    
    @property
    def owner(self):
        return self._owner


# =============================================================================
# TESTS FOR helpers.py
# =============================================================================

class TestSanitizeHtml(TestCase):
    """Tests for sanitize_html function"""
    
    def test_sanitize_removes_javascript(self):
        unsafe_html = '<script>alert("XSS")</script><p>Safe content</p>'
        result = sanitize_html(unsafe_html)
        self.assertNotIn('script', result.lower())
        self.assertIn('Safe content', result)
    
    def test_sanitize_empty_input(self):
        result = sanitize_html('')
        self.assertEqual(result, '')
    
    def test_sanitize_preserves_safe_html(self):
        safe_html = '<p>Hello <strong>World</strong></p>'
        result = sanitize_html(safe_html)
        self.assertIn('Hello', result)
        self.assertIn('World', result)


class TestGetClientIp(TestCase):
    
    def test_get_ip_from_x_forwarded_for(self):
        # Create a stub request with predefined META
        stub_request = FakeRequest(meta={
            'HTTP_X_FORWARDED_FOR': '192.168.1.100, 10.0.0.1'
        })
        result = get_client_ip(stub_request)
        self.assertEqual(result, '192.168.1.100')
    
    def test_get_ip_from_remote_addr(self):
        stub_request = FakeRequest(meta={
            'REMOTE_ADDR': '127.0.0.1'
        })
        result = get_client_ip(stub_request)
        self.assertEqual(result, '127.0.0.1')
    
    def test_get_ip_no_headers(self):
        stub_request = FakeRequest(meta={})
        result = get_client_ip(stub_request)
        self.assertIsNone(result)


class TestGetSessionUser(TestCase):
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('testuser', password='testpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
    
    def test_get_session_user_success(self):
        """Test successful user retrieval"""
        request = FakeRequest()
        request.user = self.user
        result = get_session_user(request)
        self.assertEqual(result, self.pytition_user)
    
    def test_get_session_user_not_found(self):
        """Test user not found raises Http404"""
        request = FakeRequest()
        request.user = Mock()
        request.user.username = 'nonexistent_user'
        
        with self.assertRaises(Http404):
            get_session_user(request)


class TestCheckUserInOrga(TestCase):
    """Tests for check_user_in_orga function"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('orguser', password='testpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.org = Organization.objects.create(name="TestOrg")
    
    def test_user_in_organization(self):
        """Test user is in organization"""
        self.org.members.add(self.pytition_user)
        result = check_user_in_orga(self.pytition_user, self.org)
        self.assertIsNone(result)
    
    def test_user_not_in_organization(self):
        """Test user not in organization returns HttpResponseForbidden"""
        result = check_user_in_orga(self.pytition_user, self.org)
        self.assertIsInstance(result, HttpResponseForbidden)


class TestPetitionFromId(TestCase):
    """Tests for petition_from_id function"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('petuser', password='testpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.petition = Petition.objects.create(title="Test Petition", user=self.pytition_user)
    
    def test_petition_exists(self):
        """Test petition retrieval by valid ID"""
        result = petition_from_id(self.petition.id)
        self.assertEqual(result, self.petition)
    
    def test_petition_not_exists(self):
        """Test petition not found raises Http404"""
        with self.assertRaises(Http404):
            petition_from_id(99999)


class TestRemoveUserModerated(TestCase):
    """Tests for remove_user_moderated function using FAKES"""
    
    def test_remove_moderated_petitions(self):
        """FAKE: Test filtering of moderated petitions"""
        # Create fake petitions with different moderation states
        fake_petitions = [
            FakePetition(moderated=False),
            FakePetition(moderated=True),
            FakePetition(moderated=False),
        ]
        
        result = remove_user_moderated(fake_petitions)
        self.assertEqual(len(result), 2)
    
    def test_all_moderated(self):
        """FAKE: Test when all petitions are moderated"""
        fake_petitions = [
            FakePetition(moderated=True),
            FakePetition(moderated=True),
        ]
        # Nastavíme is_moderated explicitne
        for p in fake_petitions:
            p.is_moderated = True
        
        result = remove_user_moderated(fake_petitions)
        self.assertEqual(len(result), 0)


class TestSendConfirmationEmail(TestCase):
    """Tests for send_confirmation_email using MOCKS"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('emailuser', password='testpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.petition = Petition.objects.create(
            title="Email Test Petition",
            user=self.pytition_user,
            confirmation_email_reply="reply@test.com"
        )
        self.signature = Signature.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            petition=self.petition
        )
    
    @patch('petition.helpers.get_connection')
    @patch('petition.helpers.EmailMultiAlternatives')
    def test_send_confirmation_email_called(self, mock_email_class, mock_get_connection):
        """MOCK: Test that email is sent with correct parameters"""
        # Setup mocks
        mock_connection = MagicMock()
        mock_get_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_get_connection.return_value.__exit__ = Mock(return_value=False)
        
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email
        
        # Create fake request
        request = FakeRequest(scheme='https', host='example.com')
        
        # Call the function
        send_confirmation_email(request, self.signature)
        
        # Verify email was created and sent
        mock_email_class.assert_called_once()
        mock_email.attach_alternative.assert_called_once()
        mock_email.send.assert_called_once_with(fail_silently=False)


class TestSendWelcomeMail(TestCase):
    """Tests for send_welcome_mail using MOCKS"""
    
    @patch('petition.helpers.get_connection')
    @patch('petition.helpers.EmailMultiAlternatives')
    def test_send_welcome_mail(self, mock_email_class, mock_get_connection):
        """MOCK: Test welcome mail is sent correctly"""
        mock_connection = MagicMock()
        mock_get_connection.return_value.__enter__ = Mock(return_value=mock_connection)
        mock_get_connection.return_value.__exit__ = Mock(return_value=False)
        
        mock_email = MagicMock()
        mock_email_class.return_value = mock_email
        
        user_infos = {
            'email': 'newuser@test.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        send_welcome_mail(user_infos)
        
        mock_email_class.assert_called_once()
        mock_email.send.assert_called_once_with(fail_silently=False)


class TestSubscribeToNewsletter(TestCase):
    """Tests for subscribe_to_newsletter using MOCKS"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('newsletteruser', password='testpass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
    
    @patch('petition.helpers.requests.post')
    def test_subscribe_post_method(self, mock_post):
        """MOCK: Test newsletter subscription via POST"""
        petition = Petition.objects.create(
            title="Newsletter Petition",
            user=self.pytition_user,
            newsletter_subscribe_method="POST",
            newsletter_subscribe_http_url="https://newsletter.test/subscribe",
            newsletter_subscribe_http_mailfield="email"
        )
        
        subscribe_to_newsletter(petition, "test@example.com")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://newsletter.test/subscribe")
    
    @patch('petition.helpers.requests.get')
    def test_subscribe_get_method(self, mock_get):
        """MOCK: Test newsletter subscription via GET"""
        petition = Petition.objects.create(
            title="Newsletter GET Petition",
            user=self.pytition_user,
            newsletter_subscribe_method="GET",
            newsletter_subscribe_http_url="https://newsletter.test/subscribe",
            newsletter_subscribe_http_mailfield="email"
        )
        
        subscribe_to_newsletter(petition, "test@example.com")
        
        mock_get.assert_called_once()
    
    def test_subscribe_empty_url(self):
        """Test subscription with empty URL does nothing"""
        petition = Petition.objects.create(
            title="Empty URL Petition",
            user=self.pytition_user,
            newsletter_subscribe_method="POST",
            newsletter_subscribe_http_url=""
        )
        
        # Should not raise any exception
        subscribe_to_newsletter(petition, "test@example.com")


# =============================================================================
# TESTS FOR models.py
# =============================================================================

class TestOrganizationIsLastAdmin(TestCase):
    """Tests for Organization.is_last_admin method"""
    
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user('admin1', password='pass')
        self.user2 = User.objects.create_user('admin2', password='pass')
        self.pu1 = PytitionUser.objects.get(user=self.user1)
        self.pu2 = PytitionUser.objects.get(user=self.user2)
        self.org = Organization.objects.create(name="AdminTestOrg")
    
    def test_single_admin_is_last(self):
        """Test single admin is identified as last admin"""
        self.org.members.add(self.pu1)
        perm = Permission.objects.get(organization=self.org, user=self.pu1)
        perm.can_modify_permissions = True
        perm.save()
        
        self.assertTrue(self.org.is_last_admin(self.pu1))
    
    def test_multiple_admins_not_last(self):
        """Test user is not last admin when there are multiple admins"""
        self.org.members.add(self.pu1)
        self.org.members.add(self.pu2)
        
        perm1 = Permission.objects.get(organization=self.org, user=self.pu1)
        perm1.can_modify_permissions = True
        perm1.save()
        
        perm2 = Permission.objects.get(organization=self.org, user=self.pu2)
        perm2.can_modify_permissions = True
        perm2.save()
        
        self.assertFalse(self.org.is_last_admin(self.pu1))
    
    def test_user_not_admin(self):
        """Test user without admin rights is not last admin"""
        self.org.members.add(self.pu1)
        self.org.members.add(self.pu2)
        
        perm1 = Permission.objects.get(organization=self.org, user=self.pu1)
        perm1.can_modify_permissions = True
        perm1.save()
        
        # pu2 is not an admin
        self.assertFalse(self.org.is_last_admin(self.pu2))


class TestOrganizationIsAllowedTo(TestCase):
    """Tests for Organization.is_allowed_to method"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('permuser', password='pass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.org = Organization.objects.create(name="PermTestOrg")
    
    def test_user_has_permission(self):
        """Test user with specific permission"""
        self.org.members.add(self.pytition_user)
        perm = Permission.objects.get(organization=self.org, user=self.pytition_user)
        perm.can_create_petitions = True
        perm.save()
        
        self.assertTrue(self.org.is_allowed_to(self.pytition_user, 'can_create_petitions'))
    
    def test_user_lacks_permission(self):
        """Test user without specific permission"""
        self.org.members.add(self.pytition_user)
        perm = Permission.objects.get(organization=self.org, user=self.pytition_user)
        perm.can_delete_petitions = False
        perm.save()
        
        self.assertFalse(self.org.is_allowed_to(self.pytition_user, 'can_delete_petitions'))
    
    def test_user_not_member(self):
        """Test non-member has no permissions"""
        self.assertFalse(self.org.is_allowed_to(self.pytition_user, 'can_create_petitions'))


class TestPetitionTransferTo(TestCase):
    """Tests for Petition.transfer_to method"""
    
    def setUp(self):
        User = get_user_model()
        self.user1 = User.objects.create_user('transferuser1', password='pass')
        self.user2 = User.objects.create_user('transferuser2', password='pass')
        self.pu1 = PytitionUser.objects.get(user=self.user1)
        self.pu2 = PytitionUser.objects.get(user=self.user2)
        self.org = Organization.objects.create(name="TransferOrg")
        self.petition = Petition.objects.create(title="Transfer Petition", user=self.pu1)
    
    def test_transfer_to_user(self):
        """Test transferring petition to another user"""
        self.petition.transfer_to(user=self.pu2)
        self.petition.refresh_from_db()
        
        self.assertEqual(self.petition.user, self.pu2)
        self.assertIsNone(self.petition.org)
    
    def test_transfer_to_org(self):
        """Test transferring petition to organization"""
        self.petition.transfer_to(org=self.org)
        self.petition.refresh_from_db()
        
        self.assertEqual(self.petition.org, self.org)
        self.assertIsNone(self.petition.user)
    
    def test_transfer_to_none_raises(self):
        """Test transfer with no target raises ValueError"""
        with self.assertRaises(ValueError):
            self.petition.transfer_to()
    
    def test_transfer_to_both_raises(self):
        """Test transfer with both user and org raises ValueError"""
        with self.assertRaises(ValueError):
            self.petition.transfer_to(user=self.pu2, org=self.org)


class TestPetitionPrepopulateFromTemplate(TestCase):
    """Tests for Petition.prepopulate_from_template method"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('templateuser', password='pass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        
        self.template = PetitionTemplate.objects.create(
            name="Test Template",
            user=self.pytition_user,
            text="Template text content",
            twitter_description="Twitter desc from template",
            target=1000,
            has_newsletter=True
        )
        
        self.petition = Petition.objects.create(
            title="Prepopulate Test",
            user=self.pytition_user
        )
    
    def test_prepopulate_copies_fields(self):
        """Test that fields are copied from template"""
        self.petition.prepopulate_from_template(self.template, exclude_fields=[])
        
        self.assertEqual(self.petition.text, "Template text content")
        self.assertEqual(self.petition.twitter_description, "Twitter desc from template")
        self.assertEqual(self.petition.target, 1000)
        self.assertTrue(self.petition.has_newsletter)
    
    def test_prepopulate_with_exclude(self):
        """Test prepopulation with excluded fields"""
        self.petition.prepopulate_from_template(
            self.template,
            fields=['text', 'target', 'has_newsletter'],
            exclude_fields=['target']
        )
        
        self.assertEqual(self.petition.text, "Template text content")
        self.assertNotEqual(self.petition.target, 1000)  # Should not be copied


class TestPetitionPublishUnpublish(TestCase):
    """Tests for Petition.publish and unpublish methods"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('publishuser', password='pass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.petition = Petition.objects.create(
            title="Publish Test",
            user=self.pytition_user,
            published=False
        )
    
    def test_publish_sets_date(self):
        """Test publish sets publication_date"""
        self.petition.publish()
        self.petition.refresh_from_db()
        
        self.assertTrue(self.petition.published)
        self.assertIsNotNone(self.petition.publication_date)
    
    def test_unpublish_clears_date(self):
        """Test unpublish clears publication_date"""
        self.petition.publish()
        self.petition.unpublish()
        self.petition.refresh_from_db()
        
        self.assertFalse(self.petition.published)
        self.assertIsNone(self.petition.publication_date)


class TestSignatureConfirm(TestCase):
    """Tests for Signature.confirm method"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('siguser', password='pass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        self.petition = Petition.objects.create(
            title="Signature Test",
            user=self.pytition_user
        )
    
    def test_confirm_signature(self):
        """Test signature confirmation"""
        signature = Signature.objects.create(
            first_name="Test",
            last_name="Signer",
            email="signer@test.com",
            petition=self.petition,
            confirmed=False
        )
        
        signature.confirm()
        self.assertTrue(signature.confirmed)


class TestPytitionUserModerate(TestCase):
    """Tests for PytitionUser.moderate method"""
    
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('moduser', password='pass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
    
    def test_moderate_user(self):
        """Test moderating a user"""
        self.pytition_user.moderate(True)
        self.pytition_user.refresh_from_db()
        self.assertTrue(self.pytition_user.moderated)
    
    def test_unmoderate_user(self):
        """Test unmoderating a user"""
        self.pytition_user.moderated = True
        self.pytition_user.save()
        
        self.pytition_user.moderate(False)
        self.pytition_user.refresh_from_db()
        self.assertFalse(self.pytition_user.moderated)


# =============================================================================
# TESTS FOR views.py (using RequestFactory with MOCKS)
# =============================================================================

class TestIndexView(TestCase):
    """Tests for index view using MOCKS and STUBS"""
    
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user('indexuser', password='pass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
    
    @patch.object(settings, 'INDEX_PAGE', 'ALL_PETITIONS')
    @patch.object(settings, 'PAGINATOR_COUNT', 10)
    def test_index_all_petitions(self):
        """STUB: Test index with ALL_PETITIONS setting"""
        from petition.views import index
        
        # Create some petitions
        Petition.objects.create(title="Public Petition 1", user=self.pytition_user, published=True)
        Petition.objects.create(title="Public Petition 2", user=self.pytition_user, published=True)
        
        request = self.factory.get('/')
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = index(request)
        self.assertEqual(response.status_code, 200)


class TestSearchView(TestCase):
    """Tests for search view"""
    
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user('searchuser', password='pass')
        self.pytition_user = PytitionUser.objects.get(user=self.user)
        
        Petition.objects.create(
            title="Climate Change Petition",
            text="Save the environment",
            user=self.pytition_user,
            published=True
        )
    
    def test_search_with_query(self):
        """Test search with valid query"""
        from petition.views import search
        
        request = self.factory.get('/search/', {'q': 'Climate'})
        request.user = Mock()
        request.user.is_authenticated = False
        
        response = search(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Climate', response.content)
