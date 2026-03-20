"""
Initial migration – Cithara Domain Layer
Generated for Exercise 3, Task 3.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        # User
        migrations.CreateModel(
            name='User',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email',         models.EmailField(max_length=254, unique=True)),
                ('name',          models.CharField(max_length=255)),
                ('google_id',     models.CharField(blank=True, help_text='Populated for Google OAuth users (FR-01).', max_length=255, null=True, unique=True)),
                ('password_hash', models.CharField(blank=True, help_text='Populated for manual-login users (FR-02).', max_length=255, null=True)),
                ('created_at',    models.DateTimeField(auto_now_add=True)),
                ('last_login_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),

        # Song
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id',              models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner',           models.ForeignKey(help_text='C-1: A Song belongs to exactly one User.', on_delete=django.db.models.deletion.CASCADE, related_name='songs', to='domain.user')),
                ('title',           models.CharField(max_length=255)),
                ('genre',           models.CharField(choices=[('Pop', 'Pop'), ('Rock', 'Rock'), ('Jazz', 'Jazz'), ('Classical', 'Classical'), ('Hiphop', 'Hiphop')], max_length=50)),
                ('mood',            models.CharField(choices=[('Happy', 'Happy'), ('Sad', 'Sad'), ('Romantic', 'Romantic'), ('Energetic', 'Energetic'), ('Calm', 'Calm')], max_length=50)),
                ('occasion',        models.CharField(choices=[('Birthday', 'Birthday'), ('Wedding', 'Wedding'), ('Graduation', 'Graduation'), ('Anniversary', 'Anniversary'), ('Custom', 'Custom')], max_length=50)),
                ('voice_type',      models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
                ('custom_story',    models.TextField(blank=True, help_text='Optional (FR-13). Max 1,000 characters (C-5).', null=True)),
                ('prompt_used',     models.TextField(blank=True, help_text='Stored on Song for display without joining back to request (US-17).', null=True)),
                ('audio_file_path', models.CharField(blank=True, help_text='C-7: Only populated when GenerationStatus = Completed.', max_length=1024, null=True)),
                ('duration',        models.IntegerField(blank=True, help_text='Duration in seconds. Only populated after successful generation (C-7).', null=True)),
                ('status',          models.CharField(choices=[('Pending', 'Pending'), ('InProgress', 'In Progress'), ('Completed', 'Completed'), ('Failed', 'Failed'), ('TimedOut', 'Timed Out'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('creation_date',   models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Song', 'verbose_name_plural': 'Songs', 'ordering': ['-creation_date']},
        ),

        # MusicGenerationRequest
        migrations.CreateModel(
            name='MusicGenerationRequest',
            fields=[
                ('id',               models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user',             models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generation_requests', to='domain.user')),
                ('song',             models.ForeignKey(blank=True, help_text='Populated once a Song is successfully produced (0..* → 0..1).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generation_requests', to='domain.song')),
                ('title',            models.CharField(help_text='C-4: Mandatory.', max_length=255)),
                ('genre',            models.CharField(choices=[('Pop', 'Pop'), ('Rock', 'Rock'), ('Jazz', 'Jazz'), ('Classical', 'Classical'), ('Hiphop', 'Hiphop')], max_length=50)),
                ('mood',             models.CharField(choices=[('Happy', 'Happy'), ('Sad', 'Sad'), ('Romantic', 'Romantic'), ('Energetic', 'Energetic'), ('Calm', 'Calm')], max_length=50)),
                ('voice_type',       models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10)),
                ('occasion',         models.CharField(choices=[('Birthday', 'Birthday'), ('Wedding', 'Wedding'), ('Graduation', 'Graduation'), ('Anniversary', 'Anniversary'), ('Custom', 'Custom')], max_length=50)),
                ('custom_story',     models.TextField(blank=True, help_text='Optional (FR-13). Max 1,000 characters (C-5).', null=True)),
                ('prompt_generated', models.TextField(blank=True, help_text='The prompt constructed and sent to Suno AI (FR-17).', null=True)),
                ('submitted_at',     models.DateTimeField(auto_now_add=True)),
                ('is_retry',         models.BooleanField(default=False, help_text='True when this is a regeneration attempt (FR-24).')),
                ('status',           models.CharField(choices=[('Pending', 'Pending'), ('InProgress', 'In Progress'), ('Completed', 'Completed'), ('Failed', 'Failed'), ('TimedOut', 'Timed Out'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('error_message',    models.TextField(blank=True, help_text='Populated only on failure/timeout/rejection. Null on success (FR-18, FR-49).', null=True)),
            ],
            options={'verbose_name': 'Music Generation Request', 'verbose_name_plural': 'Music Generation Requests', 'ordering': ['-submitted_at']},
        ),

        # ShareLink
        migrations.CreateModel(
            name='ShareLink',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song',       models.OneToOneField(help_text='C-8: Composition – ShareLink is deleted with its Song.', on_delete=django.db.models.deletion.CASCADE, related_name='share_link', to='domain.song')),
                ('token',      models.CharField(max_length=255, unique=True)),
                ('share_url',  models.CharField(max_length=2048)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, help_text='Reserved for future link-expiry (Open Issue 5). Currently null (Assumption 5).', null=True)),
                ('is_active',  models.BooleanField(default=True, help_text='Set False when the parent Song is deleted (FR-41).')),
            ],
            options={'verbose_name': 'Share Link', 'verbose_name_plural': 'Share Links'},
        ),

        # Feedback
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user',          models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='domain.user')),
                ('song',          models.ForeignKey(blank=True, help_text='Optional – feedback may not reference a specific song.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedbacks', to='domain.song')),
                ('feedback_text', models.TextField()),
                ('submitted_at',  models.DateTimeField(auto_now_add=True)),
                ('is_reviewed',   models.BooleanField(default=False, help_text='Internal flag for TA/admin review.')),
            ],
            options={'verbose_name': 'Feedback', 'verbose_name_plural': 'Feedbacks', 'ordering': ['-submitted_at']},
        ),
    ]
