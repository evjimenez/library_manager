document.getElementById('id_loan').addEventListener('change', function() {
    const id_loan = this.value;
    if (id_loan) {
        fetch(`/returns/get_loan_books/${id_loan}`)
            .then(response => response.json())
            .then(books => {
                const booksContainer = document.getElementById('books_container');
                const booksList = document.getElementById('books_list');
                if (books && books.length > 0) {
                    booksList.innerHTML = books.map(book => `
                        <div class="mb-3">
                            <strong>${book.title}</strong> (${book.quantity} copias)
                            <div class="input-group">
                                <span class="input-group-text">Cantidad a devolver:</span>
                                <input type="number" class="form-control" name="books_to_return[${book.id_book}]" 
                                       min="0" max="${book.quantity}" value="0">
                            </div>
                        </div>
                    `).join('');
                    booksContainer.style.display = 'block';
                } else {
                    booksList.innerHTML = '<p>No hay libros disponibles para devolver.</p>';
                    booksContainer.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const booksList = document.getElementById('books_list');
                booksList.innerHTML = '<p>Error al cargar los libros. Por favor, intente de nuevo.</p>';
                document.getElementById('books_container').style.display = 'block';
            });
    } else {
        document.getElementById('books_container').style.display = 'none';
    }
});