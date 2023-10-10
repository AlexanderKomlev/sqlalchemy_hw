import json
import sqlalchemy
import os
from sqlalchemy.orm import sessionmaker
from models import create_table, Publisher, Book, Shop, Stock, Sale

if __name__ == '__main__':
    login = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')
    database = os.getenv('DATABASE')
    DSN = f'postgresql://{login}:{password}@localhost:5432/{database}'
    engine = sqlalchemy.create_engine(DSN)
    create_table(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    with open('fixtures/tests_data.json', 'r') as file:
        data = json.load(file)

    for record in data:
        model = {
            'publisher': Publisher,
            'book': Book,
            'shop': Shop,
            'stock': Stock,
            'sale': Sale
        }[record.get('model')]
        session.add(model(id=record.get('pk'), **record.get('fields')))
    session.commit()

    i = input('Введите имя или идентификатор издателя: ')
    subq = session.query(Stock).join(Shop.stock).subquery()
    subq2 = session.query(Stock).join(Sale.stock).subquery()
    q = (session.query(Publisher).join(Book.publisher).join(subq2, Book.id == subq2.c.id_book)
         .join(subq, Book.id == subq.c.id_book))
    if i.isdigit():
        for p in q.filter(Publisher.id == i):
            for b in p.books:
                for s in b.stock:
                    for sl in s.sales:
                        print(f'{b.title.center(45)} | {s.shops.name.center(15)} | {sl.price}\t | {sl.date_sale}')
    else:
        for p in q.filter(Publisher.name.ilike(i)):
            for b in p.books:
                for s in b.stock:
                    for sl in s.sales:
                        print(f'{b.title} | {s.shops.name} | {sl.price} | {sl.date_sale}')

    session.close()
