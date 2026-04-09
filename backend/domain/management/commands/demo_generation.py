"""
Management command: demo_generation
=====================================
Demonstrates the Strategy Pattern by running either the mock or Suno strategy
directly, without needing a running server or real database records.

Usage:
    # Run mock strategy (default):
    python manage.py demo_generation

    # Run with explicit mock:
    GENERATOR_STRATEGY=mock python manage.py demo_generation

    # Run Suno strategy (requires SUNO_AI_API_KEY):
    GENERATOR_STRATEGY=suno SUNO_AI_API_KEY=<your-key> python manage.py demo_generation

    # Pass a custom title/prompt:
    python manage.py demo_generation --title "Happy Birthday Song" --prompt "Upbeat pop for a 30th birthday"
"""

from django.core.management.base import BaseCommand

from domain.generation import GenerationRequest, get_strategy


class Command(BaseCommand):
    help = "Demonstrate the active song generation strategy (mock or suno)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--title",
            default="My Test Song",
            help="Song title to use in the demo request.",
        )
        parser.add_argument(
            "--prompt",
            default="Style: Pop, Happy | Occasion/Theme: Birthday",
            help="Prompt string to send to the strategy.",
        )

    def handle(self, *args, **options):
        title = options["title"]
        prompt = options["prompt"]

        strategy = get_strategy()
        self.stdout.write(
            self.style.NOTICE(f"\n=== Active strategy: {strategy} ===\n")
        )

        request = GenerationRequest(
            request_id=0,          # 0 = demo (no real DB record)
            title=title,
            prompt=prompt,
            genre="Pop",
            mood="Happy",
            voice_type="Female",
            occasion="Birthday",
        )

        self.stdout.write(f"Submitting generation request…")
        result = strategy.generate(request)

        if result.success:
            self.stdout.write(self.style.SUCCESS("\n✔ Generation succeeded!"))
            self.stdout.write(f"  task_id  : {result.task_id}")
            self.stdout.write(f"  audio_url: {result.audio_url}")
            if result.metadata:
                self.stdout.write(f"  metadata : {result.metadata}")
        else:
            self.stdout.write(self.style.ERROR(f"\n✘ Generation failed: {result.error}"))
