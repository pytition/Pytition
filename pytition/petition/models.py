from django.db import models
from django.utils.html import mark_safe, strip_tags
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.hashers import get_hasher
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from tinymce import models as tinymce_models
from colorfield.fields import ColorField

from .helpers import sanitize_html

import html


# ----------------------------------- PytitionUser ----------------------------
class PytitionUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pytitionuser")
    invitations = models.ManyToManyField('Organization', related_name="invited", blank=True)
    default_template = models.ForeignKey('PetitionTemplate', blank=True, null=True, related_name='+', verbose_name=ugettext_lazy("Default petition template"), to_field='id', on_delete=models.SET_NULL)

    def drop(self):
        """
        Removes all the data from the organization.

        Args:
            self: (todo): write your description
        """
        with transaction.atomic():
            orgs = list(self.organization_set.all())
            petitions = list(self.petition_set.all())
            templates = list(self.petitiontemplate_set.all())
            self.delete()
            for org in orgs:
                if org.members.count() == 0:
                    org.delete()
            for petition in petitions:
                petition.delete()
            for template in templates:
                template.delete()

    @property
    def is_authenticated(self):
        """
        Returns true if the user is authenticated

        Args:
            self: (todo): write your description
        """
        return self.user.is_authenticated

    @property
    def name(self):
        """
        The name of this user.

        Args:
            self: (todo): write your description
        """
        return self.username

    @property
    def username(self):
        """
        Returns the username of the user.

        Args:
            self: (todo): write your description
        """
        return self.user.username

    @property
    def get_full_name(self):
        """
        Returns full name of the user

        Args:
            self: (todo): write your description
        """
        return self.user.get_full_name()

    @property
    def fullname(self):
        """
        Returns the fullname : class : class :.

        Args:
            self: (todo): write your description
        """
        return self.get_full_name

    @property
    def kind(self):
        """
        Return the kind of this node.

        Args:
            self: (todo): write your description
        """
        return "user"

    def __str__(self):
        """
        Returns the username of the username

        Args:
            self: (todo): write your description
        """
        if self.get_full_name != '':
            return self.get_full_name
        else:
            return self.username

    def __repr__(self):
        """
        Return the username of the object.

        Args:
            self: (todo): write your description
        """
        if self.get_full_name != '':
            return self.get_full_name
        else:
            return self.username


# --------------------------------- Organization ------------------------------
class Organization(models.Model):
    name = models.CharField(max_length=200, verbose_name=ugettext_lazy("Name"), unique=True, null=False, blank=False)
    default_template = models.ForeignKey('PetitionTemplate', blank=True, null=True, related_name='+', verbose_name=ugettext_lazy("Default petition template"), to_field='id', on_delete=models.SET_NULL)
    slugname = models.SlugField(max_length=200, unique=True)
    members = models.ManyToManyField(PytitionUser, through='Permission')

    def is_last_admin(self, user):
        """
        Check if the given user is the last admin of this organization
        Admin is an user having the can_modify_permissions right
        Return true or false
        """
        # get all permissions
        perms = Permission.objects.filter(can_modify_permissions=True, organization=self)
        if perms.count() > 1:
            return False
        elif perms.count() == 1:
            if perms.first().user == user:
                return True
            else:
                return False
        else:
            # That should never happen
            return True

    def is_allowed_to(self, user, right):
        """
        Check if an user has a given access right on the organisation
        """
        try:
            perm = Permission.objects.get(
                organization=self,
                user=user)
        except Permission.DoesNotExist:
            return False
        else:
            return getattr(perm, right)

    def __str__(self):
        """
        Return the string representation of this object.

        Args:
            self: (todo): write your description
        """
        return self.name

    def __repr__(self):
        """
        Return a human - friendly name.

        Args:
            self: (todo): write your description
        """
        return '< {} >'.format(self.name)

    @property
    def owners(self):
        """
        Returns the list of users.

        Args:
            self: (todo): write your description
        """
        return self.members.filter(permission__can_modify_permissions=True)

    @property
    def kind(self):
        """
        Return the kind of this node.

        Args:
            self: (todo): write your description
        """
        return "org"

    @property
    def fullname(self):
        """
        Returns the full name of this field.

        Args:
            self: (todo): write your description
        """
        return self.name

    def save(self, *args, **kwargs):
        """
        Custom save method.

        Args:
            self: (todo): write your description
        """
        if not self.slugname:
            self.slugname = slugify(self.name)
        super(Organization, self).save(*args, **kwargs)


# ----------------------------------- Petition --------------------------------
class Petition(models.Model):
    NO =           "no gradient"
    RIGHT =        "to right"
    BOTTOM =       "to bottom"
    BOTTOM_RIGHT = "to bottom right"
    BOTTOM_LEFT =  "to bottom left"

    LINEAR_GRADIENT_CHOICES = (
        (NO,           "no gradient"),
        (RIGHT,        "to right"),
        (BOTTOM,       "to bottom"),
        (BOTTOM_RIGHT, "to bottom right"),
        (BOTTOM_LEFT,  "to bottom left")
    )

    MAIL = "MAIL"
    POST = "POST"
    GET = "GET"

    NEWSLETTER_SUBSCRIBE_METHOD_CHOICES = (
        (MAIL, "MAIL"),
        (POST, "POST"),
        (GET,  "GET")
    )

    # Description
    title = models.TextField(verbose_name=ugettext_lazy("Title"))
    text = tinymce_models.HTMLField(blank=True)
    side_text = tinymce_models.HTMLField(blank=True)
    target = models.IntegerField(default=500)
    # Owner
    user = models.ForeignKey(PytitionUser, on_delete=models.CASCADE, null=True, blank=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    # Colors
    linear_gradient_direction = models.CharField(choices=LINEAR_GRADIENT_CHOICES, max_length=15, default=NO, blank=True)
    gradient_from = ColorField(blank=True)
    gradient_to = ColorField(blank=True)
    bgcolor = ColorField(blank=True)
    footer_text = tinymce_models.HTMLField(blank=True)
    footer_links = tinymce_models.HTMLField(blank=True)
    twitter_description = models.CharField(max_length=200, blank=True)
    twitter_image = models.CharField(max_length=500, blank=True)
    has_newsletter = models.BooleanField(default=False)
    newsletter_subscribe_http_data = models.TextField(blank=True)
    newsletter_subscribe_http_mailfield = models.CharField(max_length=100, blank=True)
    newsletter_subscribe_http_url = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_subject = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_from = models.CharField(max_length=500, blank=True)
    newsletter_subscribe_mail_to = models.CharField(max_length=500, blank=True)
    newsletter_subscribe_method = models.CharField(choices=NEWSLETTER_SUBSCRIBE_METHOD_CHOICES, max_length=4, default=MAIL)
    newsletter_subscribe_mail_smtp_host = models.CharField(max_length=100, default='localhost', blank=True)
    newsletter_subscribe_mail_smtp_port = models.IntegerField(default=25, blank=True)
    newsletter_subscribe_mail_smtp_user = models.CharField(max_length=200, blank=True)
    newsletter_subscribe_mail_smtp_password = models.CharField(max_length=200, blank=True)
    newsletter_subscribe_mail_smtp_tls = models.BooleanField(default=False)
    newsletter_subscribe_mail_smtp_starttls = models.BooleanField(default=False)
    org_twitter_handle = models.CharField(max_length=20, blank=True)
    published = models.BooleanField(default=False)
    newsletter_text = models.CharField(max_length=1000, blank=True)
    sign_form_footer = models.TextField(blank=True)
    confirmation_email_reply = models.CharField(max_length=100, blank=True)
    salt = models.TextField(blank=True)
    paper_signatures = models.IntegerField(default=0)
    paper_signatures_enabled = models.BooleanField(default=False)
    creation_date = models.DateTimeField(blank=True)
    last_modification_date = models.DateTimeField(blank=True)

    def transfer_to(self, user=None, org=None):
        """
        Transfer the organization to the organization.

        Args:
            self: (todo): write your description
            user: (todo): write your description
            org: (array): write your description
        """
        if user is None and org is None:
            raise ValueError("You should specify either an org or a user when transferring a petition")
        if user is not None and org is not None:
            raise ValueError("You cannot specify both a user and an org to transfer a petition to")
        if user:
            self.user = user
            self.org = None
        if org:
            self.org = org
            self.user = None
        self.save()

    def prepopulate_from_template(self, template, fields=None):
        """
        Prepopulate template.

        Args:
            self: (todo): write your description
            template: (str): write your description
            fields: (list): write your description
        """
        if fields is None:
            fields = [f.name for f in self._meta.fields if f.name not in ["id", "title", "salt", "user", "org"]]
        for field in fields:
            if hasattr(self, field) and hasattr(template, field):
                template_value = getattr(template, field)
                if template_value is not None and template_value != "":
                    setattr(self, field, template_value)


    def slugify(self):
        """
        Add slug. slug.

        Args:
            self: (todo): write your description
        """
        # Slugify the petition title and save it as slugname
        if self.slugmodel_set.count() == 0:
            slugtext = slugify(self.title)
            self.add_slug(slugtext)

    def add_slug(self, slugtext):
        """
        Adds slug to slug.

        Args:
            self: (todo): write your description
            slugtext: (str): write your description
        """
        # Add a slug corectly
        with transaction.atomic():
            slugtext = slugify(slugtext)
            # Check if there is another similar slug for the same user/org
            same_slugs = SlugModel.objects.filter(slug=slugtext)
            if len(same_slugs) == 0:
                slug = SlugModel.objects.create(slug=slugtext, petition=self)
            else:
                alread_used = False
                for s in same_slugs:
                    if self.owner_type == "org":
                        if s.petition.owner_type == "org":
                            if self.org == s.petition.org:
                                alread_used = True
                    else:
                        if s.petition.owner_type == "user":
                            if self.user == s.petition.user:
                                alread_used = True
                if alread_used:
                    raise ValueError('This slug is already used')
                else:
                    slug = SlugModel.objects.create(slug=slugtext, petition=self)

    def del_slug(self, slug):
        """
        Deletes a slug.

        Args:
            self: (todo): write your description
            slug: (str): write your description
        """
        # Delete a given slug
        s = SlugModel.objects.filter(slug=slug, petition=self).first()
        s.delete()

    @classmethod
    def by_id(cls, id):
        """
        Get a : class by its id.

        Args:
            cls: (todo): write your description
            id: (int): write your description
        """
        try:
            return Petition.objects.get(pk=id)
        except Petition.DoesNotExist:
            return None

    def get_signature_number(self, confirmed=None):
        """
        Return the signature number

        Args:
            self: (todo): write your description
            confirmed: (todo): write your description
        """
        signatures = self.signature_set
        if confirmed is not None:
            signatures = signatures.filter(confirmed=confirmed)
        nb_electronic_signatures = signatures.count()
        if self.paper_signatures_enabled:
            return nb_electronic_signatures + self.paper_signatures
        else:
            return nb_electronic_signatures

    def already_signed(self, email):
        """
        Returns the signed signed signed signed signed signed signed signed signed signed signed signed signed signed signed signed signature.

        Args:
            self: (todo): write your description
            email: (str): write your description
        """
        signature_number = Signature.objects.filter(petition = self.id)\
            .filter(confirmed = True).filter(email = email).count()
        return signature_number > 0

    def confirm_signature(self, conf_hash):
        """
        Confirm a signature.

        Args:
            self: (todo): write your description
            conf_hash: (todo): write your description
        """
        signature = Signature.objects.filter(petition=self.id).get(confirmation_hash=conf_hash)
        if signature:
            # Now confirm the signature corresponding to this hash
            signature.confirm()
            signature.save()
            return _("Thank you for confirming your signature!")
        else:
            return None

    def publish(self):
        """
        Publish the published published published

        Args:
            self: (todo): write your description
        """
        self.published = True
        self.save()

    def unpublish(self):
        """
        Unpublish the document

        Args:
            self: (todo): write your description
        """
        self.published = False
        self.save()

    @property
    def to_json(self):
        """
        Serialize this image to a json dict.

        Args:
            self: (todo): write your description
        """
        return {'title': self.title,
                'signatures': self.get_signature_number(True),
                'text': self.text,
                'target': self.target,
                'description': self.twitter_description,
                'image': self.twitter_image,
                'org_twitter_handle': self.org_twitter_handle,
                'has_newsletter': self.has_newsletter,
                'creator': self.owner_name}

    @property
    def owner_type(self):
        """
        The owner type of the owner.

        Args:
            self: (todo): write your description
        """
        if self.org:
            return "org"
        else:
            return "user"

    @property
    def owner_name(self):
        """
        Returns the name of the owner.

        Args:
            self: (todo): write your description
        """
        return str(self.owner)

    @property
    def owner_username(self):
        """
        Returns the owner of the user.

        Args:
            self: (todo): write your description
        """
        if self.owner_type == "org":
            return self.org.slugname
        else:
            return self.user.username

    @property
    def owner(self):
        """
        Return the owner of the organization.

        Args:
            self: (todo): write your description
        """
        if self.org:
            return self.org
        else:
            return self.user

    @property
    def signature_number(self):
        """
        Return the number of the signature.

        Args:
            self: (todo): write your description
        """
        return self.get_signature_number(True)

    @property
    def raw_twitter_description(self):
        """
        Strip html markup.

        Args:
            self: (todo): write your description
        """
        return html.unescape(mark_safe(strip_tags(sanitize_html(self.twitter_description))))

    @property
    def raw_text(self):
        """
        Parse html.

        Args:
            self: (todo): write your description
        """
        return html.unescape(mark_safe(strip_tags(sanitize_html(self.text))))

    def __str__(self):
        """
        Returns a string representation of the string.

        Args:
            self: (todo): write your description
        """
        return self.title

    def __repr__(self):
        """
        Return a human - like representation.

        Args:
            self: (todo): write your description
        """
        return self.title

    def is_allowed_to_edit(self, user):
        """
        Check if a user is allowed to edit this petition
        """
        if self.owner_type == "user":
            if self.user == user:
                # The user is the owner of the petition
                return True
            else:
                return False
        else:
            # But it is an org petition
            try:
                perm = Permission.objects.get(
                    organization=self.org,
                    user=user
                )
            except Permission.DoesNotExist:
                # No such permission, denied
                return False
            else:
                return perm.can_modify_petitions

    @property
    def url(self):
        """
        Returns the url for this slug.

        Args:
            self: (todo): write your description
        """
        slugs = self.slugmodel_set.all()
        if len(slugs) == 0:
            # If there is no slug, ugly url
            return reverse('detail', kwargs={'petition_id': self.id})
        else:
            if self.owner_type == "org":
                #  This petition is owned by an Organization
                return reverse("slug_show_petition",
                           kwargs={"orgslugname": self.org.slugname,
                               "petitionname": slugs[0]})
            elif self.owner_type == "user":
                # This petition is owned by a PytitionUser
                return reverse("slug_show_petition",
                           kwargs={"username": self.user.username,
                               "petitionname": slugs[0]})
            else:
                # This is a BUG!
                raise ValueError(_("This petition is buggy. Sorry about that!"))

    def save(self, *args, **kwargs):
        """
        Saves the current user s owner.

        Args:
            self: (todo): write your description
        """
        if (self.org is None and self.user is None):
            raise Exception("You need to provide a user or org as owner")
        elif (self.org is not None and self.user is not None):
            raise Exception("A petition can have only one owner")
        else:
            if not self.salt:
                hasher = get_hasher()
                self.salt = hasher.salt().decode('utf-8')
        self.last_modification_date = timezone.now()
        super(Petition, self).save(*args, **kwargs)


# --------------------------------- Signature ---------------------------------
class Signature(models.Model):
    first_name = models.CharField(max_length=50, verbose_name=ugettext_lazy("First name"))
    last_name = models.CharField(max_length=50, verbose_name=ugettext_lazy("Last name"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=ugettext_lazy("Phone number"))
    email = models.EmailField(verbose_name=ugettext_lazy("Email address"))
    confirmation_hash = models.CharField(max_length=128)
    confirmed = models.BooleanField(default=False, verbose_name=ugettext_lazy("Confirmed"))
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, verbose_name=ugettext_lazy("Petition"))
    subscribed_to_mailinglist = models.BooleanField(default=False, verbose_name=ugettext_lazy("Subscribed to mailing list"))
    date = models.DateTimeField(blank=True, auto_now_add=True, verbose_name=ugettext_lazy("Date"))
    ipaddress = models.TextField(blank=True, null=True)

    def clean(self):
        """
        Ensure the signed identities.

        Args:
            self: (todo): write your description
        """
        if self.petition.already_signed(self.email):
            if self.petition.signature_set.filter(email = self.email).get(confirmed = True).id != self.id:
                raise ValidationError(_("You already signed the petition"))

    def save(self, *args, **kwargs):
        """
        Custom save method

        Args:
            self: (todo): write your description
        """
        self.clean()
        if self.confirmed:
            # invalidating other signatures from same email
            Signature.objects.filter(petition=self.petition).filter(email=self.email)\
                .exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    def confirm(self):
        """
        Confirm the next confirmation.

        Args:
            self: (todo): write your description
        """
        self.confirmed = True

    def __str__(self):
        """
        Return a human - readable string.

        Args:
            self: (todo): write your description
        """
        return html.unescape("[{}:{}] {} {}".format(self.petition.id, "OK" if self.confirmed else "..", self.first_name,
                                                    self.last_name))

    def __repr__(self):
        """
        Return a human - friendly representation.

        Args:
            self: (todo): write your description
        """
        return html.unescape("[{}:{}] {} {}".format(self.petition.id, "OK" if self.confirmed else "..", self.first_name,
                                                    self.last_name))


#------------------------------- PetitionTemplate -----------------------------
class PetitionTemplate(models.Model):
    NO =           "no gradient"
    RIGHT =        "to right"
    BOTTOM =       "to bottom"
    BOTTOM_RIGHT = "to bottom right"
    BOTTOM_LEFT =  "to bottom left"

    LINEAR_GRADIENT_CHOICES = (
        (NO,           "no gradient"),
        (RIGHT,        "to right"),
        (BOTTOM,       "to bottom"),
        (BOTTOM_RIGHT, "to bottom right"),
        (BOTTOM_LEFT,  "to bottom left")
    )

    MAIL = "MAIL"
    POST = "POST"
    GET = "GET"

    NEWSLETTER_SUBSCRIBE_METHOD_CHOICES = (
        (MAIL, "MAIL"),
        (POST, "POST"),
        (GET,  "GET")
    )

    # Description
    name = models.CharField(max_length=50, verbose_name=ugettext_lazy("Name"))
    text = tinymce_models.HTMLField(blank=True)
    side_text = tinymce_models.HTMLField(blank=True)
    target = models.IntegerField(blank=True, null=True)
    # Owner
    user = models.ForeignKey(PytitionUser, on_delete=models.CASCADE, null=True, blank=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    # Fancy colors
    linear_gradient_direction = models.CharField(choices=LINEAR_GRADIENT_CHOICES, max_length=15, default=NO, blank=True)
    gradient_from = ColorField(blank=True)
    gradient_to = ColorField(blank=True)
    bgcolor = ColorField(blank=True)
    footer_text = tinymce_models.HTMLField(blank=True)
    footer_links = tinymce_models.HTMLField(blank=True)
    twitter_description = models.CharField(max_length=200, blank=True)
    twitter_image = models.CharField(max_length=500, blank=True)
    has_newsletter = models.BooleanField(default=False)
    newsletter_subscribe_http_data = models.TextField(blank=True)
    newsletter_subscribe_http_mailfield = models.CharField(max_length=100, blank=True)
    newsletter_subscribe_http_url = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_subject = models.CharField(max_length=1000, blank=True)
    newsletter_subscribe_mail_from = models.EmailField(max_length=500, blank=True)
    newsletter_subscribe_mail_to = models.EmailField(max_length=500, blank=True)
    newsletter_subscribe_method = models.CharField(choices=NEWSLETTER_SUBSCRIBE_METHOD_CHOICES, max_length=4,
                                                   default=MAIL)
    newsletter_subscribe_mail_smtp_host = models.CharField(max_length=100, default='localhost', blank=True)
    newsletter_subscribe_mail_smtp_port = models.IntegerField(default=25)
    newsletter_subscribe_mail_smtp_user = models.CharField(max_length=200, blank=True)
    newsletter_subscribe_mail_smtp_password = models.CharField(max_length=200, blank=True)
    newsletter_subscribe_mail_smtp_tls = models.BooleanField(default=False)
    newsletter_subscribe_mail_smtp_starttls = models.BooleanField(default=False)
    org_twitter_handle = models.CharField(max_length=20, blank=True)
    newsletter_text = models.CharField(max_length=1000, blank=True)
    sign_form_footer = models.TextField(blank=True)
    confirmation_email_reply = models.EmailField(max_length=100, blank=True)
    use_custom_email_settings = models.BooleanField(default=False)

    def __str__(self):
        """
        Return the string representation of this object.

        Args:
            self: (todo): write your description
        """
        return self.name

    def __repr__(self):
        """
        Return the __repr__ method.

        Args:
            self: (todo): write your description
        """
        return self.name

    @property
    def owner_type(self):
        """
        The owner type of the owner.

        Args:
            self: (todo): write your description
        """
        if self.org:
            return "org"
        else:
            return "user"

    def save(self, *args, **kwargs):
        """
        Custom save **

        Args:
            self: (todo): write your description
        """
        if (self.org is None and self.user is None):
            raise Exception("You need to provide a user or org as owner")
        elif (self.org is not None and self.user is not None):
            raise Exception("A petition can have only one owner")
        else:
            super(PetitionTemplate, self).save(*args, **kwargs)


# --------------------------------- SlugModel ---------------------------------
class SlugModel(models.Model):
    slug = models.SlugField(max_length=200)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE)

    def clean(self, *args, **kwargs):
        """
        Ensure that slug is unique.

        Args:
            self: (todo): write your description
        """
        if self.slug == "" or self.slug is None:
            raise ValidationError(_("A permlink cannot be empty. Please enter something."), code="invalid")
        super(SlugModel, self).clean(*args, **kwargs)

    def __str__(self):
        """
        Return the string representation of the string.

        Args:
            self: (todo): write your description
        """
        return self.slug

    def __repr__(self):
        """
        Return a representation of this field.

        Args:
            self: (todo): write your description
        """
        return self.slug

# ------------------------------------ Permission -----------------------------
class Permission(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name=ugettext_lazy("Organization related to these permissions"))
    user = models.ForeignKey(PytitionUser, on_delete=models.CASCADE, verbose_name=ugettext_lazy("User related to these permissions"))
    can_add_members = models.BooleanField(default=False)
    can_remove_members = models.BooleanField(default=False)
    can_create_petitions = models.BooleanField(default=True)
    can_modify_petitions = models.BooleanField(default=True)
    can_delete_petitions = models.BooleanField(default=False)
    can_create_templates = models.BooleanField(default=True)
    can_modify_templates = models.BooleanField(default=True)
    can_delete_templates = models.BooleanField(default=False)
    can_view_signatures = models.BooleanField(default=False)
    can_modify_signatures = models.BooleanField(default=False)
    can_delete_signatures = models.BooleanField(default=False)
    can_modify_permissions = models.BooleanField(default=False)

    def set_all(self, value):
        """
        Sets the value of the field.

        Args:
            self: (todo): write your description
            value: (todo): write your description
        """
        self.can_add_members = value
        self.can_remove_members = value
        self.can_create_petitions = value
        self.can_modify_petitions = value
        self.can_delete_petitions = value
        self.can_create_templates = value
        self.can_modify_templates = value
        self.can_delete_templates = value
        self.can_view_signatures = value
        self.can_modify_signatures = value
        self.can_delete_signatures = value
        self.can_modify_permissions = value
        self.save()

    def __str__(self):
        """
        Returns the organization name.

        Args:
            self: (todo): write your description
        """
        return "{} : {}".format(self.organization.name, self.user.name)

    def __repr__(self):
        """
        Return a repr representation of - repr repr.

        Args:
            self: (todo): write your description
        """
        return '< {} >'.format(self.__str__())


#------------------------------ Pre save actions -----------------------------
@receiver(pre_save, sender=SlugModel)
def check_slug_is_not_empty(sender, instance, **kwargs):
    """
    Validate that the slug is not empty.

    Args:
        sender: (todo): write your description
        instance: (todo): write your description
    """
    instance.clean()
    instance.validate_unique()

#------------------------------ Post save actions -----------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a user profile.

    Args:
        sender: (todo): write your description
        instance: (todo): write your description
        created: (bool): write your description
    """
    if created:
        PytitionUser.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    Save user profile.

    Args:
        sender: (todo): write your description
        instance: (todo): write your description
    """
    instance.pytitionuser.save()

@receiver(pre_save, sender=Petition)
def pre_save_petition(sender, instance, **kwargs):
    """
    Pre - save save save save_date.

    Args:
        sender: (todo): write your description
        instance: (todo): write your description
    """
    if not instance.creation_date:
        instance.creation_date = timezone.now()

@receiver(post_save, sender=Petition)
def save_petition(sender, instance, **kwargs):
    """
    Saves save ** save_pet.

    Args:
        sender: (todo): write your description
        instance: (todo): write your description
    """
    if instance.slugmodel_set.count() == 0:
        instance.slugify()
    if kwargs['created']:
        instance.creation_date = timezone.now()
        instance.save()

@receiver(post_delete, sender=PytitionUser)
def post_delete_user(sender, instance, *args, **kwargs):
    """
    Post - user instance.

    Args:
        sender: (todo): write your description
        instance: (todo): write your description
    """
    if instance.user:  # just in case user is not specified
        instance.user.delete()
