# macropad
Ce logiciel est mon soft personnel pour mon macropad personnelle

## Layout
Les boutons envois l*X*c*Y* sur le port série à l'appuis d'un switch mécanique.
Exemple :
| *X* / *Y* | 1    | 2    |
|:---------:|:----:|:----:|
| 1         | l1c1 | l1c2 |
| 2         | l2c1 | l2c2 |

Et pour les encodeurs voici la logique :
| Sens de rotation | Commande      |
|:----------------:|:-------------:|
| Horaire          | e*X*+         |
| Anti-Horaire     | e*X*-         |
| Bouton poussoir  | e*X*b         |

*Avec X qui est égale au numéro de l'encodeur*  

## Règles Yml
| Type     | Value  | Description                                                      |
|:--------:|:------:|:-----------------------------------------------------------------|
| key      | string | Exécute des touches de clavier (ex : "ctrl c")                   |
| text     | string | Ecrit du text (ex: "hello world !")                              |
| delay    | int    | Fais une pause en ms (ex: "100")                                 |
| command  | string | Lance une commande dans un terminal (ex: "echo 'hello world !'") |
| macropad | object | Gestion interne du macropad (ex: profil+)                         |


## Fichier config.js
```json
{
    "SerialPort" : "",
    "pythonCmd" : ""
}

```
