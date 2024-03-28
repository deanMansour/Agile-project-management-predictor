# Generated by Django 5.0.2 on 2024-03-11 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Predicting_app', '0002_excel_file_data_excel_row_data_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='excel_row_data',
            name='affects_versions',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='assignee',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='created',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='fix_versions',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='issue_id',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='issue_key',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='issue_type',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='last_viewed',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='original_estimate',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='original_estimate_currency',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='parent_id',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='priority',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='project_description',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='project_key',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='project_name',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='project_type',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='project_url',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='remaining_estimate',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='remaining_estimate_currency',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='reporter',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='resolution',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='resolved',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='status',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='summary',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='time_spent',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='time_spent_currency',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='updated',
        ),
        migrations.RemoveField(
            model_name='excel_row_data',
            name='work_ratio',
        ),
        migrations.AddField(
            model_name='excel_row_data',
            name='json_data',
            field=models.JSONField(null=True),
        ),
    ]