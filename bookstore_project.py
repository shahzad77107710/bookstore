import streamlit as st
from datetime import datetime

class Book:
    def __init__(self, id, title, stock, price, author="Unknown", description=""):
        self.id = id
        self.title = title
        self.stock = stock
        self.price = price
        self.author = author
        self.description = description
        self.added_date = datetime.now().date()

class BookStore:
    def __init__(self):
        if 'books' not in st.session_state:
            st.session_state.books = [
                Book(1, "Python Basics", 10, 250, "John Doe", "Introduction to Python programming"),
                Book(2, "AI & ML", 5, 400, "Jane Smith", "Fundamentals of AI and Machine Learning"),
                Book(3, "Data Science", 8, 300, "Alex Johnson", "Data analysis and visualization"),
                Book(4, "Web Development", 6, 350, "Sarah Williams", "Building modern web applications"),
                Book(5, "Cyber Security", 4, 500, "Mike Brown", "Cybersecurity principles and practices")
            ]
        
        if 'admin_username' not in st.session_state:
            st.session_state.admin_username = "admin"
            st.session_state.admin_password = "1234"
        
        if 'cart' not in st.session_state:
            st.session_state.cart = []
        
        if 'sales_history' not in st.session_state:
            st.session_state.sales_history = []
        
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        
        if 'admin_logged_in' not in st.session_state:
            st.session_state.admin_logged_in = False

    def show_all_books(self, books=None):
        books_to_display = books if books else st.session_state.books
        st.subheader("📚 Available Books")
        
        book_data = []
        for book in sorted(books_to_display, key=lambda x: x.id):
            book_data.append({
                "ID": book.id,
                "Title": book.title,
                "Author": book.author,
                "Stock": book.stock,
                "Price": f"Rs.{book.price}",
                "Description": book.description[:30] + "..." if len(book.description) > 30 else book.description
            })
        
        st.table(book_data)

    def search_books(self):
        st.subheader("🔍 Search Books")
        term = st.text_input("Enter search term (title/author/description):").lower()
        
        if term:
            found = [b for b in st.session_state.books 
                    if term in b.title.lower() 
                    or term in b.author.lower() 
                    or term in b.description.lower()]
            
            if found:
                st.success(f"Found {len(found)} books:")
                self.show_all_books(found)
            else:
                st.warning("No books found matching your search.")

    def add_to_cart(self):
        st.subheader("🛍️ Add to Cart")
        self.show_all_books()
        
        book_id = st.number_input("Enter Book ID to add to cart:", min_value=1, step=1)
        book = next((b for b in st.session_state.books if b.id == book_id), None)
        
        if book:
            if book.stock > 0:
                quantity = st.number_input(
                    f"Enter quantity (Available: {book.stock})", 
                    min_value=1, 
                    max_value=book.stock,
                    step=1
                )
                
                if st.button("Add to Cart"):
                    # Check if book already in cart
                    cart_item = next((item for item in st.session_state.cart if item['book'].id == book.id), None)
                    if cart_item:
                        cart_item['quantity'] += quantity
                        cart_item['subtotal'] += quantity * book.price
                    else:
                        st.session_state.cart.append({
                            "book": book,
                            "quantity": quantity,
                            "subtotal": quantity * book.price
                        })
                    st.success(f"Added {quantity} x '{book.title}' to cart")
            else:
                st.warning("Sorry, this book is out of stock.")
        elif book_id > 0:
            st.error("Invalid Book ID.")

    def view_cart(self):
        st.subheader("🛒 Your Cart")
        
        if not st.session_state.cart:
            st.info("Your cart is empty")
            return
            
        cart_data = []
        total = 0
        for item in st.session_state.cart:
            cart_data.append({
                "Title": item['book'].title,
                "Quantity": item['quantity'],
                "Price": f"Rs.{item['book'].price}",
                "Subtotal": f"Rs.{item['subtotal']}"
            })
            total += item['subtotal']
        
        st.table(cart_data)
        st.subheader(f"💵 Total: Rs.{total}")

    def checkout(self):
        st.subheader("💰 Checkout")
        
        if not st.session_state.cart:
            st.warning("Your cart is empty")
            return
            
        self.view_cart()
        
        with st.form("checkout_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            
            if st.form_submit_button("Confirm Purchase"):
                # Process purchase
                for item in st.session_state.cart:
                    item['book'].stock -= item['quantity']
                
                # Record sale
                sale = {
                    "date": datetime.now(),
                    "customer": {"name": name, "email": email},
                    "items": [{"title": item['book'].title, "quantity": item['quantity'], 
                              "price": item['book'].price} for item in st.session_state.cart],
                    "total": sum(item['subtotal'] for item in st.session_state.cart)
                }
                st.session_state.sales_history.append(sale)
                
                # Generate receipt
                self.generate_receipt(sale)
                
                st.session_state.cart = []
                st.success("Thank you for your purchase!")

    def generate_receipt(self, sale):
        st.subheader("🧾 Receipt")
        st.write(f"**Date:** {sale['date'].strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Customer:** {sale['customer']['name']} ({sale['customer']['email']})")
        
        st.write("\n**Items Purchased:**")
        for item in sale['items']:
            st.write(f"- {item['quantity']} x {item['title']} @ Rs.{item['price']}")
        
        st.write(f"\n**Total:** Rs.{sale['total']}")
        st.write("\nThank you for shopping with us!")

    def admin_login(self):
        st.subheader("🔐 Admin Login")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username == st.session_state.admin_username and password == st.session_state.admin_password:
                st.session_state.admin_logged_in = True
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error("Invalid credentials")

    def admin_panel(self):
        st.subheader("🔐 Admin Panel")
        
        tabs = ["Add New Book", "Edit Book", "Remove Book", "View Sales"]
        selected_tab = st.radio("Select action:", tabs)
        
        if selected_tab == "Add New Book":
            self.add_new_book()
        elif selected_tab == "Edit Book":
            self.edit_book()
        elif selected_tab == "Remove Book":
            self.remove_book()
        elif selected_tab == "View Sales":
            self.view_sales()
        
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

    def add_new_book(self):
        st.subheader("📘 Add New Book")
        
        with st.form("add_book_form"):
            title = st.text_input("Title")
            author = st.text_input("Author")
            description = st.text_area("Description")
            stock = st.number_input("Stock quantity", min_value=0, step=1)
            price = st.number_input("Price", min_value=0.0, step=10.0)
            
            if st.form_submit_button("Add Book"):
                new_id = max(b.id for b in st.session_state.books) + 1 if st.session_state.books else 1
                new_book = Book(new_id, title, stock, price, author, description)
                st.session_state.books.append(new_book)
                st.success(f"Book '{title}' added successfully with ID {new_id}.")

    def edit_book(self):
        st.subheader("✏️ Edit Book")
        self.show_all_books()
        
        book_id = st.number_input("Enter Book ID to edit:", min_value=1, step=1)
        book = next((b for b in st.session_state.books if b.id == book_id), None)
        
        if book:
            st.write("\n**Current Book Details:**")
            
            with st.form("edit_book_form"):
                title = st.text_input("Title", value=book.title)
                author = st.text_input("Author", value=book.author)
                description = st.text_area("Description", value=book.description)
                stock = st.number_input("Stock", value=book.stock, min_value=0, step=1)
                price = st.number_input("Price", value=float(book.price), min_value=0.0, step=10.0)
                
                if st.form_submit_button("Update Book"):
                    book.title = title
                    book.author = author
                    book.description = description
                    book.stock = stock
                    book.price = price
                    st.success("Book updated successfully")
        elif book_id > 0:
            st.error("Book not found")

    def remove_book(self):
        st.subheader("❌ Remove Book")
        self.show_all_books()
        
        book_id = st.number_input("Enter Book ID to remove:", min_value=1, step=1)
        book = next((b for b in st.session_state.books if b.id == book_id), None)
        
        if book:
            st.warning(f"You are about to delete: {book.title}")
            if st.button("Confirm Delete"):
                st.session_state.books = [b for b in st.session_state.books if b.id != book_id]
                st.success("Book removed successfully")
        elif book_id > 0:
            st.error("Book not found")

    def view_sales(self):
        st.subheader("📊 Sales History")
        
        if not st.session_state.sales_history:
            st.info("No sales recorded yet")
            return
            
        total_revenue = 0
        total_books = 0
        
        for sale in st.session_state.sales_history:
            st.write(f"\n**📅 {sale['date'].strftime('%Y-%m-%d %H:%M')}**")
            st.write(f"👤 {sale['customer']['name']}")
            
            items_df = []
            for item in sale['items']:
                items_df.append({
                    "Title": item['title'],
                    "Quantity": item['quantity'],
                    "Price": f"Rs.{item['price']}",
                    "Subtotal": f"Rs.{item['quantity'] * item['price']}"
                })
            
            st.table(items_df)
            st.write(f"**💵 Total:** Rs.{sale['total']}")
            
            total_revenue += sale['total']
            total_books += sum(item['quantity'] for item in sale['items'])
        
        st.subheader("📈 Summary")
        st.write(f"**Total Sales:** {len(st.session_state.sales_history)}")
        st.write(f"**Total Books Sold:** {total_books}")
        st.write(f"**Total Revenue:** Rs.{total_revenue}")

    def run(self):
        st.title("📚 Python Book Store")
        
        if st.session_state.admin_logged_in:
            self.admin_panel()
            return
            
        menu = ["Show All Books", "Search Books", "Add to Cart", "View Cart", "Checkout", "Admin Login"]
        choice = st.sidebar.selectbox("Menu", menu)
        
        if choice == "Show All Books":
            self.show_all_books()
        elif choice == "Search Books":
            self.search_books()
        elif choice == "Add to Cart":
            self.add_to_cart()
        elif choice == "View Cart":
            self.view_cart()
        elif choice == "Checkout":
            self.checkout()
        elif choice == "Admin Login":
            self.admin_login()

if __name__ == "__main__":
    store = BookStore()
    store.run()