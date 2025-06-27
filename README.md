# macropad
Ce logiciel est mon soft personnel pour mon macropad personnelle

## Layout
Les boutons envois LXCY sur le port série à l'appuis d'un switch mécanique.
Exemple :
| X / Y | 1    | 2    |
|:-----:|:----:|:----:|
| 1     | L1C1 | L1C2 |
| 2     | L2C1 | L2C2 |

Et pour les encodeurs voici la logique :
| Sens de rotation | Commande    |
|:----------------:|:-----------:|
| Horaire          | EX+         |
| Anti-Horaire     | EX-         |
| Bouton poussoir  | EXB         |

*Avec X qui est égale au numéro de l'encodeur*  

## TO-DO Interface
- Créer layout selon le macropad (V4 ou V5)
- Récupération des inputs sur le port série
- Détection du boiter quand branché (pas besoin de renseigner le port)
- Exécution d'un script à l'appuis (Python / Bash)
- Intégrer éditeur de texte pour l'édition du script
- Petit bouton pour jouer le script sans l'appuis
- Intégration d'envoie d'information pour l'écran
- Gestion des profiles

## TO-DO Code embarqué
- Intégrer l'écran (affichage simple)
- Intégrer paramètre
    - Luminosité eclairage
    - ...
- Changement de profils
- Affichage commande qui va être envoyé
