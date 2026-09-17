from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("projects", "0002_project_contract_address_project_last_tx_hash_and_more")]

    operations = [
        migrations.RemoveField(model_name="project", name="contract_address"),
        migrations.RemoveField(model_name="project", name="last_tx_hash"),
        migrations.RemoveField(model_name="project", name="onchain_project_id"),
    ]
