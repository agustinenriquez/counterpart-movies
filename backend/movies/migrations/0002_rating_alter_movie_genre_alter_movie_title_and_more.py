# Generated by Django 4.2.17 on 2025-03-23 21:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Rating",
            fields=[
                (
                    "tconst",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="movies.movie",
                    ),
                ),
                (
                    "average_rating",
                    models.DecimalField(db_index=True, decimal_places=1, max_digits=3),
                ),
                ("num_votes", models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name="movie",
            name="genre",
            field=models.CharField(
                blank=True, db_index=True, max_length=200, null=True
            ),
        ),
        migrations.AlterField(
            model_name="movie",
            name="title",
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="movie",
            name="year",
            field=models.CharField(blank=True, db_index=True, max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name="name",
            name="name",
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="principal",
            name="characters",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
