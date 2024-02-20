from flask import Blueprint, jsonify, request
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json

RuffelBok_app = Blueprint("RuffelBok_app", __name__)
current_datetime = datetime.now().strftime("%Y%m%d")
book_file = f"books_{current_datetime}.json"


@RuffelBok_app.route('/', methods=['GET'])
def fetch_books():

    try:
        with open(book_file, 'r') as file:
            books = json.load(file)
    except FileNotFoundError:
        books_data = []

        for page_num in range(1, 51):
            try:
                response_obj = requests.get(f"https://books.toscrape.com/catalogue/page-{page_num}.html")
                response = response_obj.text

                if response_obj.status_code == 200:
                    print("Request successful for page", page_num)

                    soup = BeautifulSoup(response, 'html.parser')
                    books = soup.find_all('h3')
                    books_extracted = 0

                    for book in books:
                        book_url = book.find('a')['href']
                        book_response = requests.get('https://books.toscrape.com/catalogue/' + book_url)
                        book_soup = BeautifulSoup(book_response.content, 'html.parser')

                        title = book_soup.find('h1').text
                        category = book_soup.find('ul', class_="breadcrumb").find_all('a')[2].text.strip()
                        rating = book_soup.find('p', class_='star-rating')['class'][1]
                        price = book_soup.find('p', class_='price_color').text.strip()
                        price = price.replace("Â", "")
                        availability = book_soup.find('p', class_='availability').text.strip()



                        book_info = {
                        'Title': title,
                        'Category': category,
                        'Price': price,
                        'Rating': rating,
                        'Availability': availability
                        }
                        books_data.append(book_info)
                        books_extracted += 1
                        if books_extracted == 20:
                            break

                else:
                    return jsonify({"Request failed for page", page_num}), 404
            except TypeError:
                break
        with open(book_file, 'w') as file:
            json.dump(books_data, file, indent=2)
    return jsonify(books_data), 200


@RuffelBok_app.route('/<category>', methods=['GET'])
def get_book_category(category):
    category_books = []
    with open(book_file, 'r') as file:
        books = json.load(file)
        for book in books:
            if book.get('Category') == category:
                category_books.append(book)

        if not category_books:
            return jsonify({'error': 'No books found in this category!'}), 404

    try:
        file_category = f"{category}_{current_datetime}.json"
        with open(file_category, 'w') as file:
            json.dump(category_books, file, indent=2)
    except Exception as e:
        return jsonify({'error': f'Error occurred while saving JSON file: {str(e)}'}), 500
    return jsonify(category_books), 200


@RuffelBok_app.route('/<title>', methods=['DELETE'])
def delete_book(title):
    with open(book_file, 'r') as file:
        books = json.load(file)
        for book in books:
            if book['Title'] == title:
                books.remove(book)
                with open(book_file, 'w') as file:
                    json.dump(books, file, indent=2)
                return jsonify({'message': 'Book deleted successfully!'}), 200
    return jsonify({'error': 'Book not found!'}), 404


@RuffelBok_app.route('/<title>', methods=['PUT'])
def update_book(title):
    title = request.json['Title']
    category = request.json['Category']
    rating = request.json['Rating']
    price = request.json['Price']
    availability = request.json['Availability']
    with open(book_file, 'r') as file:
        books = json.load(file)
        for book in books:
            if book['Title'] == title:
                book['Category'] = category
                book['Rating'] = rating
                book['Price'] = price
                book['Availability'] = availability
                with open(book_file, 'w') as file:
                    json.dump(books, file, indent=2)
                return jsonify({'message': 'Book updated successfully!'}), 200

        return jsonify({'error': 'Book not found!'}), 404


@RuffelBok_app.route('/', methods=['POST'])
def add_book():
    with open(book_file, 'r') as file:
        books = json.load(file)
        title = request.json['Title']
        category = request.json['Category']
        rating = request.json['Rating']
        price = request.json['Price']
        availability = request.json['Availability']
        for book in books:
            if book['Title'] == title:
                return jsonify({'error': 'Book already exists!'}), 400
        new_book = {
            'Title': title,
            'Category': category,
            'Rating': rating,
            'Price': price,
            'Availability': availability
            }
        books.append(new_book)
    with open(book_file, 'w') as file:
        json.dump(books, file,indent=2)
    return jsonify({'message': 'Book added successfully!'}), 200

if __name__ == '__main__':
    RuffelBok_app.run(debug=True)



#Om man vill scrapa första sidan av hemsidan.
    
"""
def get_books_page1():
    response_obj = requests.get("https://books.toscrape.com/")
    response = response_obj.text

    if response_obj.status_code == 200:
        print("Request successful")

        soup = BeautifulSoup(response, 'html.parser')
        title = soup.find('title')
        print(title.text)

        books_data = []
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").get_text().strip()
            rating = book.p["class"][1]
            stock = book.find("p", class_="instock availability").get_text().strip()

            book_info = {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Availability": stock
            }

            books_data.append(book_info)

        with open(book_file, 'w') as file:
            json.dump(books_data, file, indent=2)

        for book in books_data:
            print(f"Title: {book['Title']}")
            print(f"Price: {book['Price']}")
            print(f"Rating: {book['Rating']}")
            print(f"availability: {book['availability']}\n")

    else:
        return jsonify({"Request failed}), 404

    return jsonify(books_data), 200
"""