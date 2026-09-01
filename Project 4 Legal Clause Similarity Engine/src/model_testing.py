from gensim.models import Word2Vec

MODEL_PATH =r"models/legal_word2vec.model"

model = Word2Vec.load(MODEL_PATH)

vocabulary = list(model.wv.index_to_key)
print("Vocabulary Size:",len(vocabulary))

print("\nFirst 20 Words:")
print(vocabulary[:20])

#Checking whether the Specific Word eists

word ="tenant"

if word in model.wv:
    print(f"\n'{word}' exists in the vocabulary.")

else:
    print(f"\n'{word}' does not exist in the vocabulary.")

#Fetching vector for a word

vector = model.wv["tenant"]

print("\nVector for 'tenant':")

print(vector)

#Fidning Similar Words

similar_words = model.wv.most_similar("tenant",topn=10)

print("\nWords Similar to 'tenant':")

for word,score in similar_words:
    print(word,score)