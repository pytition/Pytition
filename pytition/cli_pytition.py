#!/usr/bin/env python3
import argparse
import os
import sys


def get_parser():
    parser = argparse.ArgumentParser("cli_pytition")
    subparsers = parser.add_subparsers(help='sub-command help', dest="action")
    genorga = subparsers.add_parser("gen_orga", help="create Pytition Organization")
    genorga.add_argument("--orga", "-o", type=str, required=True)
    genusers = subparsers.add_parser("gen_user", help="create Pytition user")
    genusers.add_argument("--username", "-u", type=str, required=True)
    genusers.add_argument("--first-name", "-f", type=str, required=True)
    genusers.add_argument("--last-name", "-l", type=str, required=True)
    genusers.add_argument("--password", "-p", type=str, required=False, default="f00bar")
    join_org = subparsers.add_parser("join_org", help="make a Pytition user join an Organization")
    join_org.add_argument("--orga", "-o", type=str, required=True)
    join_org.add_argument("--user", "-u", type=str, required=True)
    genpet = subparsers.add_parser("generate_petitions", help="Generate petitions")
    genpet.add_argument("--number", "-n", help="petition number", type=int, required=True)
    genpet.add_argument("--orga", "-o", type=str, required=False)
    genpet.add_argument("--user", "-u", type=str, required=False)
    gensignature = subparsers.add_parser("generate_signatures", help="Generate signatures")
    gensignature.add_argument("--number", "-n", help="number of signatures", type=int, default=1)
    gensignature.add_argument("--petition-id", "-i", help="petition id", type=int)
    gensignature.add_argument("--petition-title", "-t", help="petition title", type=str)
    gensignature.add_argument("--first-name", help="first name of the signatory", type=str, default="bob")
    gensignature.add_argument("--last-name", help="last name of the signatory", type=str, default="Bar")
    gensignature.add_argument("--email", help="mail of the signatory", type=str, default="bob@bar.com")
    return parser


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pytition.settings")
    import django
    django.setup()
    from petition.models import Petition, Organization, PytitionUser, Permission, Signature

    args = get_parser().parse_args()

    if args.action == "join_org":
        username = args.user
        orgname = args.orga
        u = PytitionUser.objects.get(user__username=username)
        org = Organization.objects.get(name=orgname)
        print("user: {}".format(u))
        print("orga: {}".format(org))
        org.members.add(u)
        org.save()
        perms = Permission.objects.get(organization=org, user=u)
        perms.can_add_members = True
        perms.can_remove_members = True
        perms.can_create_petitions = True
        perms.can_modify_petitions = True
        perms.can_delete_petitions = True
        perms.can_view_signatures = True
        perms.can_modify_signatures = True
        perms.can_delete_signatures = True
        perms.can_modify_permissions = True
        perms.save()
    elif args.action == "generate_petitions":
        if args.orga == None and args.user == None:
            print("You must either specify --orga or --user")
            sys.exit(1)
        if args.number:
            for i in range(args.number):
                if args.orga:
                    orgname = args.orga
                    orga = Organization.objects.get(name=orgname)
                    p = Petition.objects.create(title="Petition"+str(i), text="blabla"+str(i), org_twitter_handle="@RAP_Asso", published=True, org=orga)
                elif args.user:
                    username = args.user
                    u = PytitionUser.objects.get(user__username=username)
                    p = Petition.objects.create(title="Petition"+str(i), text="blabla"+str(i), org_twitter_handle="@RAP_Asso", published=True, user=u)
    elif args.action == "gen_user":
        from django.contrib.auth.models import User
        user = User.objects.create_user(args.username, password=args.password)
        user.is_staff = True
        if args.first_name:
            user.first_name = args.first_name
        if args.last_name:
            user.last_name = args.last_name
        user.save()
    elif args.action == "gen_orga":
        org = Organization.objects.create(name=args.orga)
        org.save()
    elif args.action == "generate_signatures":
        if args.petition_id is not None:
            petition = Petition.objects.get(id=args.petition_id)
        elif args.petition_title is not None:
            try:
                petition = Petition.objects.get(title=args.petition_title)
            except django.core.exceptions.MultipleObjectsReturned:
                print("multitple petition match this title, choose it by id")
                sys.exit(1)
        else:
            print("You must either specify --petition-id or --petition-title")
            sys.exit(1)

        for i in range(args.number):
            signature = Signature.objects.create(
                first_name=args.first_name,
                last_name=args.last_name,
                email=args.email,
                petition=petition
            )
    else:
        print("You should chose an action, see --help for more information")


if __name__ == "__main__":
	main()
