from petition.models import Organization, Petition, PytitionUser, Permission
from django.contrib.auth import get_user_model


def add_default_data():
    """
    Add default data for test purpose
    """
    users = ['julia', 'john', 'max', 'sarah']
    orgs = ['RAP', 'Greenpeace', 'Attac', 'Les Amis de la Terre']
    user_published_petitions = {
        'john': 0,
        'sarah': 0,
        'julia': 5,
        'max': 10
    }
    user_unpublished_petitions = {
        'john': 0,
        'sarah': 5,
        'julia': 0,
        'max': 10
    }
    org_published_petitions = {
        'RAP': 0,
        'Les Amis de la Terre': 0,
        'Greenpeace': 1,
        'Attac': 2
    }
    org_unpublished_petitions = {
        'RAP': 0,
        'Les Amis de la Terre': 1,
        'Greenpeace': 0,
        'Attac': 2
    }
    org_members = {
        'RAP': ['julia'],
        'Les Amis de la Terre': ['julia', 'max'],
        'Attac': ['john'],
    }
    org_admins = {
        'RAP': ['julia'],
        'Les Amis de la Terre': ['julia'],
        'Attac': ['john'],
    }
    User = get_user_model()
    for org in orgs:
        o = Organization.objects.create(name=org)
        for i in range(org_published_petitions[org]):
            p = Petition.objects.create(
                    published=True,
                    title="Petition A%i" % i,
                    org=o
            )
        for i in range(org_unpublished_petitions[org]):
            p = Petition.objects.create(
                published=False,
                title="Petition B%i" % i,
                org=o
            )
    for user in users:
        u = User.objects.create_user(user, password=user)
        u.first_name = user
        u.save()
        pu = PytitionUser.objects.get(user__username=user)
        for i in range(user_published_petitions[user]):
            p = Petition.objects.create(
                    published=True,
                    title="Petition C%i" % i,
                    user=pu
                )
        for i in range(user_unpublished_petitions[user]):
            p = Petition.objects.create(
                published=False,
                title="Petition D%i" % i,
                user=pu
            )
    for orgname in org_members:
        org = Organization.objects.get(name=orgname)
        for username in org_members[orgname]:
            user = PytitionUser.objects.get(user__username=username)
            org.members.add(user)
    for orgname in org_admins:
        org = Organization.objects.get(name=orgname)
        for username in org_admins[orgname]:
            user = PytitionUser.objects.get(user__username=username)
            perms = Permission.objects.get(organization=org, user=user)
            perms.can_modify_permissions = True
            perms.save()

    admin = User.objects.create_user('admin', password='admin', is_staff=True, is_superuser=True)
