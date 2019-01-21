# sallypy
digitisation control utility (PDF/A-1b) / utilitaire de contrôle de numérisation (PDF/A-1b)

# Installation:
Déposer les fichiers dans un dossier dédié. Par exemple:
C:\ProgramFiles\cdsp\sallypy

Un fichier bat est disponible dans le repo. Il pointe directement sur le chemin donné en exemple. En double cliquant sur le bat, le script se lancera.

Si sallypy est déjà installé sur votre ordinateur, vous pouvez simplement déposer le fichier sallypy.bat sur votre bureau, par exemple, et double cliquer dessus.

# Utilisation:

Windows - avec le bat file:
Double cliquer sur le fichier bat. Les paramètres nécesaires vous seront demandés, dans l'ordre:
- le chemin vers le dossier à analyser
- le chemin vers le fichier bordereau (csv)
- (optionnel) le chemin vers le fichier de configuration du csv. Il en existe un par défaut, qui sera utilisé si vous n'en renseignez pas un.

Astuce: pour ne pas réécrire les chemins, vous pouvez drag&drop les fichiers et dossiers depuis votre gestionnaire de fichiers directement


Linux - en ligne de commande:
python sally.py /path/to/files/folder/ /path/to/bordereau/file.csv [/path/to/conf/file.json]

# Fichiers créés en sortie:
Le programme s’exécute et génère 2 tableurs dans le dossier contenant le bordereau et les fichiers numérisés : « controle_pdf_sally.csv » et « report_sally.csv ». « controle_pdf_sally » contient les résultats du contrôle sous une forme qui peut être reportée dans le bordereau de numérisation (0 si ok, 1 si erreur et nom du contrôleur Sally). « report_sally » contient le détail des erreurs.
