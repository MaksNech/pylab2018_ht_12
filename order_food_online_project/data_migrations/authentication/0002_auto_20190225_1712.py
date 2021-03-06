# Generated by Django 2.1.5 on 2019-02-25 17:12
from __future__ import unicode_literals
from django.db import migrations


# from django.contrib.auth.models import Group, Permission


def set_permissions_to_groups(apps, schema_editor):
    authors_permission_codenames = [
        'add_ingredient',
        'view_ingredient',
        'change_ingredient',
        'delete_ingredient',
        'add_dish',
        'view_dish',
        'change_dish',
        'delete_dish',
        'add_note',
        'view_note',
        'change_note',
        'delete_note',
        'view_section',
        'add_dishingredients',
        'view_dishingredients',
        'change_dishingredients',
        'delete_dishingredients',

    ]
    customers_permission_codenames = [
        'view_ingredient',
        'view_dish',
        'view_note',
        'view_section',
        'add_order',
        'view_order',
        'add_orderingredients',
        'view_orderingredients',
        'change_orderingredients',
        'delete_orderingredients',

    ]

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    authors_group, authors_group_created = Group.objects.get_or_create(name='authors')
    if authors_group:

        for codename in authors_permission_codenames:
            permission = Permission.objects.get(codename=codename)
            authors_group.permissions.add(permission)

    
    customers_group, customers_group_created = Group.objects.get_or_create(name='customers')
    if customers_group:

        for codename in customers_permission_codenames:
            permission = Permission.objects.get(codename=codename)
            customers_group.permissions.add(permission)


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_permissions_to_groups),
    ]
