import pandas as pd

# Chemins des fichiers
file_path_csv = 'src/include/library/words.csv'

# Chargement du fichier CSV existant
try:
    words_df = pd.read_csv(file_path_csv, header=None, names=["word"])
    words_list = words_df['word'].tolist()

except FileNotFoundError:
    print(f"Le fichier '{file_path_csv}' est introuvable. Un nouveau fichier sera créé.")
    words_list = []

# Listes des mots à ajouter si non présents
mots_de_liaison = [
    "et", "mais", "ou", "donc", "or", "ni", "car", "que", "parce que", "lorsque", "puisque"
]
articles_indefinis = [
    "un", "une", "des", "du", "de la", "de l'", "au", "aux"
]
conjonctions_coordination = [
    "et", "ou", "ni", "mais", "car", "or", "donc"
]
lettres_alphabet = [chr(i) for i in range(97, 123)]  # a-z
chiffres = [str(i) for i in range(0, 2051)]  # 0 à 2050

# Ajouter les éléments à la liste des mots existants
words_to_add = mots_de_liaison + articles_indefinis + conjonctions_coordination + lettres_alphabet + chiffres

# Ajouter les mots manquants à la liste
for word in words_to_add:
    if word not in words_list:
        words_list.append(word)

# Créer un DataFrame à partir de la liste de mots mise à jour
updated_words_df = pd.DataFrame({"word": words_list})

# Enregistrer le DataFrame mis à jour dans un fichier CSV
updated_words_df.to_csv(file_path_csv, index=False, header=False)
print(f"Fichier CSV '{file_path_csv}' mis à jour avec succès.")
