
from src.extractor import extract_document


sample_text = """
ТОО "Алматы Трейд Компани"

БИН 170340021554

Счёт на оплату № 1245 от 12.11.2026

Наименование                 Кол-во    Цена       Сумма

Бумага A4 80г/м2                50      2 100     105 000
Картридж HP 85A                  3     18 500      55 500

Итого:                                            160 500

НДС 16%:                                           25 680

Всего к оплате:                                   186 180 тенге
"""


result = extract_document(sample_text)

print("\nExtracted document:")
print(result.model_dump_json(indent=2))


# DOCUMENT 2 — Commercial offer (Russian)

sample_text_2 = """
Коммерческое предложение
от компании «Digital Solutions»

Уважаемый клиент! Предлагаем Вам следующие услуги:

- Разработка сайта — 450 000 тг
- Техподдержка, в месяц — 60 000 тг

Предложение действительно до 30.11.2026.
Составлено 05.11.2026.

С уважением, менеджер Айгуль.
"""


# DOCUMENT 3 — Invoice (Kazakh + Russian)

sample_text_3 = """
ЖШС «Көкжиек Құрылыс» / ТОО "Кокжиек Курулыс"

БСН/БИН: 210640900180

Шот-фактура № АКТ-09 / 09 қазан 2026 ж.

Қызмет көрсету / Оказание услуг - 1 ед. - 340 000

Жалпы сомасы: Үш жүз қырық мың теңге 00 тиын

НДС не облагается
"""


# Run extraction on all three documents

for index, text in enumerate(
    [sample_text, sample_text_2, sample_text_3],
    start=1
):
    print(f"\n{'=' * 20} DOCUMENT {index} {'=' * 20}")

    result = extract_document(text)

    print(result.model_dump_json(indent=2))
