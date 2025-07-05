   
import os
import streamlit as st
import requests

Library_File = "library.txt"
Seperator = " | "

# ------------------- Data Management -------------------
def load_Library():
    library = []
    if os.path.exists(Library_File):
        with open(Library_File, "r") as file:
            for line in file:
                if line.strip():
                    parts = line.strip().split(Seperator)
                    book = {
                        "title": parts[0],
                        "author": parts[1],
                        "year": int(parts[2]),
                        "genre": parts[3],
                        "read": parts[4] == "True",
                        "link": parts[5] if len(parts) > 5 else ""
                    }
                    library.append(book)
    return library

def save_Library(library):
    try:
        with open(Library_File, "w") as file:
            for book in library:
                line = Seperator.join([
                    book["title"],
                    book["author"],
                    str(book["year"]),
                    book["genre"],
                    str(book["read"]),
                    book["link"]
                ])
                file.write(line + "\n")
    except Exception as e:
        st.error(f"Error saving library: {e}")
        
        
def add_Book(title, author, year, genre, read, link):
    book = {
        "title": title,
        "author": author,
        "year": year,
        "genre": genre,
        "read": read,
        "link": link
    }
    st.session_state.library.append(book)
    save_Library(st.session_state.library)
    st.success("✅ Book added successfully! Switch to 'View Library' to see it.")

def remove_book(title):
    found = False
    for book in st.session_state.library:
        if book["title"].lower() == title.lower():
            st.session_state.library.remove(book)
            found = True
            break
    if found:
        save_Library(st.session_state.library)
        st.success(f"✅ Book '{title}' removed successfully.")
    else:
        st.warning("⚠️ Book not found.")

def search_book(keyword):
    keyword = keyword.lower()
    return [book for book in st.session_state.library if keyword in book["title"].lower() or keyword in book["author"].lower()]

def display_books(library):
    if not library:
        st.info("Library is empty.")
    else:
        for i, book in enumerate(library):
            col1, col2 = st.columns([4, 1])
            with col1:
                title_display = f"[{book['title']}]({book['link']})" if book['link'] else book['title']
                st.markdown(f"### {title_display}")
                st.markdown(f"**Author:** {book['author']}  \n**Year:** {book['year']}  \n**Genre:** {book['genre']}")
            
            with col2:
                # Toggle button for read status
                new_status = st.checkbox(
                    "Read", 
                    value=book["read"], 
                    key=f"read_{i}",
                    label_visibility="collapsed"
                )
                
                if new_status != book["read"]:
                    book["read"] = new_status
                    save_Library(st.session_state.library)
                    st.rerun()  # Refresh to show updated status
            
            st.markdown("---")

def display_statistics():
    total = len(st.session_state.library)
    if total == 0:
        st.warning("No books in the library.")
        return
    read_books = sum(1 for book in st.session_state.library if book["read"])
    percent_read = (read_books / total) * 100
    st.markdown(f"**📚 Total books:** {total}")
    st.markdown(f"**📖 Books read:** {read_books} ({percent_read:.2f}%)")

# ------------------- Open Library API -------------------
def fetch_from_open_library(title):
    url = f"https://openlibrary.org/search.json?title={title}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["numFound"] > 0:
            book_data = data["docs"][0]
            book_info = {
                "title": book_data.get("title", "Unknown"),
                "author": book_data["author_name"][0] if "author_name" in book_data else "Unknown",
                "year": book_data.get("first_publish_year", 0),
                "genre": "Unknown",
                "read": False,
                "link": f"https://openlibrary.org{book_data.get('key', '')}",
                "cover_id": book_data.get("cover_i", None)
            }
            return book_info
    return None

def display_book_info(book):
    st.markdown(f"### [{book['title']}]({book['link']})")
    st.markdown(f"**Author:** {book['author']}")
    st.markdown(f"**Year:** {book['year']}")
    if book['cover_id']:
        cover_url = f"https://covers.openlibrary.org/b/id/{book['cover_id']}-L.jpg"
        st.image(cover_url, width=200)

# ------------------- Streamlit UI -------------------
def main():
    st.set_page_config(page_title="📚 Library Manager", layout="centered")
    st.title("📚 Personal Library Manager")

    # Initialize session state
    if "library" not in st.session_state:
        st.session_state.library = load_Library()

    menu = ["View Library", "Add Book", "Remove Book", "Search", "Statistics", "Fetch from Open Library"]
    choice = st.sidebar.selectbox("📘 Menu", menu)

    if choice == "View Library":
        st.subheader("📖 All Books")
        display_books(st.session_state.library)

    elif choice == "Add Book":
        st.subheader("➕ Add a New Book")
        with st.form("add_form"):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            year = st.number_input("Publication Year", min_value=1, step=1)
            genre = st.text_input("Genre")
            read = st.radio("Have you read it?", ["Yes", "No"]) == "Yes"
            link = st.text_input("Book Link (optional)")
            submitted = st.form_submit_button("Add Book")
            if submitted:
                add_Book(title, author, year, genre, read, link)

    elif choice == "Remove Book":
        st.subheader("🗑️ Remove Book(s)")
    
        # Option to choose between search or view all
        remove_option = st.radio("Remove option:", 
                            ["Search for book to remove", "View all books with delete options"],
                            horizontal=True)
    
        if remove_option == "Search for book to remove":
            # Original search-based removal
            title = st.text_input("Enter book title to remove")
            if st.button("Remove"):
                remove_book(title)
    
        else:  # View all books with delete options
            if not st.session_state.library:
                st.warning("Your library is empty!")
            else:
                st.write("### All Books (Click to delete)")
                for i, book in enumerate(st.session_state.library):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{book['title']}** by {book['author']} ({book['year']})")
                    with col2:
                        if st.button("❌ Delete", key=f"del_{i}"):
                            st.session_state.library.remove(book)
                            save_Library(st.session_state.library)
                            st.success(f"Removed: {book['title']}")
                            st.rerun()  # Refresh to show updated list
                    st.markdown("---")

    # elif choice == "Search":
    #     st.subheader("🔍 Search for Books")
    #     keyword = st.text_input("Enter title or author")
    #     if keyword:
    #         results = search_book(keyword)
    #     if results:
    #         st.success(f"Found {len(results)} result(s).")
    #         display_books(results)
    #     else:
    #         st.warning("No matching books found.")
    
    elif choice == "Search":
        st.subheader("🔍 Search for Books")
        keyword = st.text_input("Enter title or author")
    
        # Initialize results as empty list
        results = []
    
        if keyword:
            results = search_book(keyword)
    
        if keyword:  # Only show results if there was a search
            if results:
                st.success(f"Found {len(results)} result(s).")
                display_books(results)
            else:
                st.warning("No matching books found.")
        else:
            st.info("👆 Enter a search term to begin")

    elif choice == "Statistics":
        st.subheader("📊 Library Statistics")
        display_statistics()

    
    elif choice == "Fetch from Open Library":
        st.subheader("🌐 Fetch Book from Open Library")
        book_title = st.text_input("Enter Book Title")
    
        if st.button("Search"):
            book = fetch_from_open_library(book_title)
            if book:
                # Store the fetched book in session state
                st.session_state.fetched_book = book
                display_book_info(book)
    
        # Check if there's a fetched book available to add
        if "fetched_book" in st.session_state:
            fetched_book = st.session_state.fetched_book
            if st.button("Add This Book"):
                add_Book(
                    fetched_book["title"],
                    fetched_book["author"],
                    fetched_book["year"],
                    fetched_book["genre"],
                    fetched_book["read"],
                    fetched_book["link"]
                )
                # Clear the fetched book after adding
                del st.session_state.fetched_book
        else:
            st.warning("No results found. Try a different title.")

if __name__ == "__main__":
    main()