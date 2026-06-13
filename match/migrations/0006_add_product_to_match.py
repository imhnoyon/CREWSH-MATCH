from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0005_alter_request_unique_together_and_more'),
        ('marketplace', '0003_product_valid_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, related_name='matches', to='marketplace.product'),
        ),
    ]
