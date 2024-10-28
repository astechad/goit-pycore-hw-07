from collections import UserDict
import re
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Ім'я не може бути порожнім")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Номер телефону має містити рівно 10 цифр")
        super().__init__(value)

    @staticmethod
    def validate(phone_number):
        return re.fullmatch(r"\d{10}", phone_number) is not None


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError(
                "Неправильний формат дати. Використовуйте DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        new_phone = Phone(phone)
        self.phones.append(new_phone)

    def delete_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return
        raise ValueError("Номер телефону не знайдено")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        return f"День народження: {self.birthday}" if self.birthday else "День народження не встановлений"

    def __str__(self):
        phones_str = "; ".join(phone.value for phone in self.phones)
        return f"Ім'я контакту: {self.name.value}, телефони: {phones_str}, {self.show_birthday()}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Запис з ім'ям '{name}' не знайдено")

    def find_record(self, name):
        return self.data.get(name, None)

    def get_upcoming_birthdays(self, days=7):
        upcoming = []
        today = datetime.now().date()
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.replace(year=today.year)
                if 0 <= (birthday - today).days <= days:
                    upcoming.append(record)
        return upcoming


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Помилка: {str(e)}"
        except KeyError:
            return "Контакт не знайдено"
        except IndexError:
            return "Недостатньо аргументів для виконання команди"
    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find_record(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find_record(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Номер телефону змінено"
    return "Контакт не знайдено"


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find_record(name)
    if record:
        return f"Телефони для {name}: " + ", ".join(phone.value for phone in record.phones)
    return "Контакт не знайдено"


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find_record(name)
    if record:
        record.add_birthday(birthday)
        return "День народження додано"
    return "Контакт не знайдено"


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find_record(name)
    if record:
        return record.show_birthday()
    return "Контакт не знайдено"


@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "Немає днів народження найближчим часом"
    result = "Найближчі дні народження:\n"
    for record in upcoming_birthdays:
        result += f"{record.name.value}: {record.birthday}\n"
    return result


def show_all(book: AddressBook):
    if not book:
        return "Адресна книга порожня"
    return "\n".join(str(record) for record in book.values())


def parse_input(user_input):
    command, *args = user_input.strip().split()
    return command, args


def main():
    book = AddressBook()
    print("Ласкаво просимо до асистента!")
    while True:
        user_input = input("Введіть команду: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("До побачення!")
            break

        elif command == "hello":
            print("Чим можу допомогти?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Неправильна команда.")


if __name__ == "__main__":
    main()
