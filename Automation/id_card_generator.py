import os
import sys
import django
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Django setup
def setup_django():
    """Configure Django settings before any Django code is imported."""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Automation.settings')
        django.setup()
        from collector.models import IDCard
        return IDCard
    except Exception as e:
        logger.error(f"Failed to configure Django: {str(e)}")
        raise

class AFITIDCardGenerator:
    def __init__(
        self,
        template_path: str = "Automation/id_template.png",
        font_path: str = "Automation/font/Arial.ttf",
        output_dir: str = "id_card_images"
    ):
        self.template_path = Path(template_path)
        self.font_path = Path(font_path)
        self.output_dir = Path(output_dir)
        self.IDCard = setup_django()
        
        # Define text positions based on AFIT template
        self.text_positions = {
            'name': (150, 655),           # NAME field
            'department': (220, 710),      # Department Field
            'gender': (150, 760),          # GENDER field
            'blood_group': (570, 760),     # BLOOD GROUP field
            'mat_number': (190, 810)       # MATRIC NO field
        }
        
        # Define image positions and sizes for passport and signature
        self.image_positions = {
            'passport': {'pos': (163, 230), 'size': (290, 340)},  # Centered passport photo
            'signature': {'pos': (200, 845), 'size': (200, 45)}   # Bottom signature
        }
        
        self._validate_paths()
        self._init_fonts()

    def _validate_paths(self) -> None:
        """Validate that all required files and directories exist."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
        if not self.font_path.exists():
            raise FileNotFoundError(f"Font file not found: {self.font_path}")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _init_fonts(self) -> None:
        """Initialize fonts for text rendering."""
        self.regular_font = ImageFont.truetype(str(self.font_path), 24)
        self.bold_font = ImageFont.truetype(str(self.font_path), 26)

    def _process_image(self, image_path: str, size: Tuple[int, int]) -> Image.Image:
        """Process and resize an image while maintaining aspect ratio."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        original = Image.open(image_path)
        # Calculate aspect ratio preserving dimensions
        aspect = original.width / original.height
        target_aspect = size[0] / size[1]
        
        if aspect > target_aspect:
            # Image is wider than needed
            new_width = int(size[1] * aspect)
            new_height = size[1]
        else:
            # Image is taller than needed
            new_width = size[0]
            new_height = int(size[0] / aspect)
            
        # Resize maintaining aspect ratio
        resized = original.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with white background
        final = Image.new('RGBA', size, (255, 255, 255, 0))
        
        # Calculate position to paste resized image centered
        paste_x = (size[0] - new_width) // 2
        paste_y = (size[1] - new_height) // 2
        
        final.paste(resized, (paste_x, paste_y))
        return final

    def generate_single_card(self, student) -> None:
        """Generate an ID card for a single student."""
        try:
            # Create a new copy of the template
            template = Image.open(self.template_path).copy()
            draw = ImageDraw.Draw(template)

            # Add text elements
            text_color = "black"  # Dark blue color for text
            for field, pos in self.text_positions.items():
                font = self.bold_font if field == 'mat_number' else self.regular_font
                value = getattr(student, field)
                if field == 'department':
                    value = str(value).upper()  # Convert department to uppercase
                draw.text(pos, str(value), font=font, fill=text_color)

            # Add passport photo
            try:
                passport = self._process_image(
                    student.passport.path,
                    self.image_positions['passport']['size']
                )
                template.paste(passport, self.image_positions['passport']['pos'], passport)
            except Exception as e:
                logger.error(f"Failed to process passport photo for {student.name}: {str(e)}")

            # Add signature
            try:
                signature = self._process_image(
                    student.signature.path,
                    self.image_positions['signature']['size']
                )
                template.paste(signature, self.image_positions['signature']['pos'], signature)
            except Exception as e:
                logger.error(f"Failed to process signature for {student.name}: {str(e)}")

            # Save the generated ID card
            output_path = self.output_dir / f"{student.mat_number}_id_card.png"
            template.save(output_path)
            logger.info(f"ID card generated successfully for {student.name}")

        except Exception as e:
            logger.error(f"Failed to generate ID card for {student.name}: {str(e)}")
            raise

    def generate_all_cards(self) -> None:
        """Generate ID cards for all students in the database."""
        students = self.IDCard.objects.all()
        total_students = students.count()
        logger.info(f"Starting ID card generation for {total_students} students")

        for index, student in enumerate(students, 1):
            try:
                self.generate_single_card(student)
                logger.info(f"Progress: {index}/{total_students}")
            except Exception as e:
                logger.error(f"Error processing student {student.name}: {str(e)}")
                continue

        logger.info("ID card generation completed")

def main():
    try:
        generator = AFITIDCardGenerator()
        generator.generate_all_cards()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()