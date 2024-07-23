from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load your data
popular_df = pickle.load(open('popular_df.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_ratings'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend_books():
    user_input = request.form.get('user_input')
    recommendations = recommend(user_input)
    return render_template('recommend.html',data=recommendations)
    
def recommend(book_name):
    if book_name not in pt.index:
        print(f"Book '{book_name}' not found in the dataset")
        return []
    
    index = np.where(pt.index == book_name)[0][0]
    
    if index >= len(similarity_scores):
        print("Index out of rangr in similarity scores")
        return []
    
    similar_items =  sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]
    
    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        
        # Ensure temp_df is not empty
        if temp_df.empty:
            print(f"No data found for book: {pt.index[i[0]]}")
            continue
        
        # Deduplicate and extract information
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        data.append(item)
    
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)