"""
AI Expense Categorization Model
Uses scikit-learn with TF-IDF and Naive Bayes for text classification
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

class ExpenseCategorizer:
    """ML model for categorizing expenses based on description"""
    
    def __init__(self):
        """Initialize the categorizer"""
        self.model = None
        self.categories = ['Food', 'Travel', 'Bills', 'Shopping', 'Entertainment']
        self.model_file = 'expense_model.pkl'

        # 🔹 ADDED (safe feature)
        self.FOOD_KEYWORDS = [
            'food','potato','chips','fries','snack','burger','pizza',
            'coffee','tea','meal','lunch','dinner','breakfast',"popcorn"
        ]
        
        # Load model if exists, otherwise will train
        if os.path.exists(self.model_file):
            self.load_model()

    # 🔹 ADDED (safe feature)
    def _food_override(self, description):
        for word in self.FOOD_KEYWORDS:
            if word in description:
                return 'Food'
        return None

    def get_training_data(self):
        training_descriptions = [
            'lunch at restaurant','dinner with friends','groceries from supermarket',
            'breakfast coffee','pizza delivery','fast food burger','sushi takeout',
            'grocery shopping','food delivery','restaurant bill','cafe latte',
            'starbucks coffee','mcdonalds meal','subway sandwich','dominos pizza',
            'ice cream','snacks chips','fruits vegetables','meat chicken',
            'bakery bread','candy chocolate','food court meal','buffet dinner',

            'uber ride','taxi fare','bus ticket','train ticket','flight booking',
            'hotel accommodation','airbnb stay','car rental','gas fuel',
            'parking fee','metro card','toll fee','airport shuttle',
            'vacation package','travel insurance','lyft ride','ola cab',
            'bike rental','road trip','cruise booking','travel visa',

            'electricity bill','water bill','internet bill','phone bill',
            'rent payment','insurance premium','credit card payment','loan emi',
            'gas bill','cable tv','netflix subscription','spotify premium',
            'gym membership','utility payment','mortgage payment','property tax',
            'youtube premium','amazon prime','hulu subscription','medical insurance',

            'clothing purchase','shoes shopping','electronics store','furniture buy',
            'book purchase','online shopping','amazon order','walmart shopping',
            'target purchase','ebay order','home decor','cosmetics beauty',
            'jewelry purchase','toy store','sports equipment','garden supplies',
            'office supplies','hardware store','pet supplies','gift purchase',
            'laptop computer','mobile phone','headphones','watch',

            'movie tickets','concert tickets','theater show','museum entry',
            'theme park','bowling alley','video games','streaming service',
            'sports event','comedy show','bar drinks','nightclub cover',
            'casino gambling','arcade games','mini golf','escape room',
            'zoo tickets','aquarium visit','festival pass','hobby class',
            'books magazine','music album','app purchase','game subscription'
        ]

        training_categories = (
            ['Food'] * 23 +
            ['Travel'] * 21 +
            ['Bills'] * 20 +
            ['Shopping'] * 24 +
            ['Entertainment'] * 24
        )

        return training_descriptions, training_categories

    def train(self):
        descriptions, categories = self.get_training_data()

        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                lowercase=True,
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])

        self.model.fit(descriptions, categories)
        self.save_model()

    def predict(self, description):
        if self.model is None:
            self.train()

        description = description.lower().strip()

        if not description:
            return 'Shopping'

        # 🔹 ADDED (safe feature)
        food_rule = self._food_override(description)
        if food_rule:
            return food_rule

        try:
            return self.model.predict([description])[0]
        except Exception as e:
            print(f"Prediction error: {e}")
            return 'Shopping'

    def predict_with_confidence(self, description):
        if self.model is None:
            self.train()

        description = description.lower().strip()

        probabilities = self.model.predict_proba([description])[0]
        return {
            category: round(prob * 100, 2)
            for category, prob in zip(self.categories, probabilities)
        }

    def save_model(self):
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.model, f)

    def load_model(self):
        with open(self.model_file, 'rb') as f:
            self.model = pickle.load(f)

    def get_categories(self):
        return self.categories


# Test
if __name__ == '__main__':
    ec = ExpenseCategorizer()
    ec.train()

    print(ec.predict("potato at gaming street shop"))  # Food
    print(ec.predict("gaming subscription"))           # Entertainment

