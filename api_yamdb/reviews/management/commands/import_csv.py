from typing import Dict, Any, Tuple, Optional, Union
import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):
    help = 'Импорт данных из файлов в модели django.'

    def handle(self, *args: Union[Tuple, Any], **kwargs: Any) -> None:
        """
        Импортирует данные из csv в модель.
        """
        CSV_DIR: Path = Path('static', 'data')
        FILE_HANDLE: Tuple[Tuple[str, Any, Dict[str, Optional[str]]], ...] = (
            ('category.csv', Category, {}),
            ('genre.csv', Genre, {}),
            ('users.csv', User, {}),
            ('titles.csv', Title, {'category': 'category_id'}),
            ('genre_title.csv', Title.genre.through, {}),
            ('review.csv', Review, {'author': 'author_id'}),
            ('comments.csv', Comment, {'author': 'author_id'}),
        )
        for file, model, replace in FILE_HANDLE:
            with open(
                Path(CSV_DIR, file),
                mode='r',
                encoding='utf8'
            ) as file_handle:
                reader = csv.DictReader(file_handle)
                objects_to_create: list[Any] = [
                    self.retrieve_model_instance(
                        row,
                        model,
                        replace
                    ) for row in reader
                ]
                model.objects.bulk_create(
                    objects_to_create,
                    ignore_conflicts=True
                )

    def retrieve_model_instance(
        self,
        row: Dict[str, Optional[str]],
        model: Any,
        replace: Dict[str, Optional[str]]
    ) -> Any:
        """
        Извлекает экземпляр модели, используя заданные данные строки,
        и обрабатывает замену имен полей.
        """
        instance_kwargs: Dict[str, Optional[str]] = {**row}
        if replace:
            for old, new in replace.items():
                instance_kwargs[new] = instance_kwargs.pop(old)
        return model(**instance_kwargs)
