document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    const bookSearch = document.getElementById('bookSearch');
    const searchResults = document.getElementById('searchResults');
    const selectedBooks = document.getElementById('selectedBooks');
    const selectedBooksInput = document.getElementById('selectedBooksInput');
    const loanForm = document.getElementById('loanForm');
    
    let selectedBooksArray = [];
    
    bookSearch.addEventListener('input', debounce(searchBooks, 300));
    
    function searchBooks() {
        const query = bookSearch.value.trim();
        console.log('buscador:', query);
        
        if (query.length === 0) {
            console.log('sin nada que buscar');
            searchResults.innerHTML = '';
            return;
        }
        
        if (query.length < 2) {
            console.log('demasiado corto');
            return;
        }
        
        console.log('resultados:', query);
        fetch(`/books/search?query=${encodeURIComponent(query)}`)
            .then(response => {
                console.log('estado:', response.status);
                return response.json();
            })

            .then(books => {
                console.log('Books received:', books);
                searchResults.innerHTML = books.map(book => `
                    <div class="list-group-item d-flex justify-content-between align-items-center py-2">
                        <span class="me-3">${book.title} - Autor: ${book.author} - Materia: ${book.materia} -  <strong>Disponibles: ${book.available}</strong></span>
                        <button class="btn btn-primary btn-sm" onclick="addBook(${book.id}, '${book.title}', ${book.available})">Agregar</button>
                    </div>
                `).join('');
            })

            .catch(error => {
                console.error('erro:', error);
            });
    }

    window.addBook = function(id, title, available) {
        console.log('agregando:', id, title, available);
        const existingBook = selectedBooksArray.find(book => book.id === id);
        if (existingBook) {
            if (existingBook.quantity < available) {
                existingBook.quantity++;
                console.log('Aumentar la Cantidad');
            } else {
                console.log('sin cantidad disponible');
                alert('No hay más copias disponibles de este libro.');
                return;
            }
        } else {
            selectedBooksArray.push({ id, title, quantity: 1 });
            console.log('Libro Agregado');
        }
        updateSelectedBooksList();
    }
    
    function updateSelectedBooksList() {
        console.log('actualiar la lista');
        selectedBooks.innerHTML = selectedBooksArray.map(book => `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                ${book.title} - Cantidad: ${book.quantity}
                <button class="btn btn-sm btn-danger" onclick="removeBook(${book.id})">Eliminar</button>
            </li>
        `).join('');
        selectedBooksInput.value = JSON.stringify(selectedBooksArray);
        console.log('libros seleccionados:', selectedBooksArray);
    }
    
    window.removeBook = function(id) {
        console.log('libros eleminados:', id);
        selectedBooksArray = selectedBooksArray.filter(book => book.id !== id);
        updateSelectedBooksList();
    }
    
    function debounce(func, delay) {
        let timeoutId;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                console.log('tiempo activo');
                func.apply(context, args);
            }, delay);
        };
    }
    
    loanForm.addEventListener('submit', function(e) {
        console.log('enviado');
        if (selectedBooksArray.length === 0) {
            console.log('comprobar libros');
            e.preventDefault();
            alert('Por favor, seleccione al menos un libro.');
        }
    });
});