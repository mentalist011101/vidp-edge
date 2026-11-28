# Texte à lire pour nos vidéos

<p align="justify">
    Bonjour à tous. Aujourd'hui vingt-huit novembre deux mille vingt-six, nous, étudiants à l'Ecole Nationale Supérieure Polytechnique de Yaoundé allons vous présenter un projet scolaire.
</p>

<p align="justify">
    Notre projet se nomme ```Vidp-edge```. Déjà ceci est un script écrit pour tester notre système d'analyse vidéo. Notre nut est de vérifier si la parole est bien transcrite dans n'importe quelle condition d'enregistrement.
</p>

<p align="justify">
    Nous allons illustrer tout ceci avec un petit exemple. 
    Imaginons, une petite entreprise basée à Yaoundé et ayant des agences dans des villes différentes : Bafoussam et Douala. Chaque agence dispose de caméras qui filment du matin au soir. Envoyer toutes les vidéos au siège, c'est-à-dire à Yaoundé, serait coûteux car la connexion internet est parfois lente, et elle peut même se couper pendant plusieurs minutes.

    Pour résoudre ce problème, les agences doivent traiter les vidéos directement sur place. Comment ? 
    - l'ordinateur de l'agence écoute la parole dans les vidéos d'enregistrement
    - transforme cette parole en texte
    - crée deux version splus légères de la vidéo :
        - une en trois cent soixante pixels
        - une autre en quatre cent vingt pixels de hauteur

    Seul l'essentiel est envoyé au siège (Yaoundé).
</p>

<p align="justify">
    Quand le réseau tombe en panne, rien n'est perdu. Les résultats attendent dans une file d'attente, sur le disque, comme des lettres dans une boîte. Dès que la connexion revient, ils partent un par un, et le siège les reçoit sans doublon.
</p>

<p align="justify">
    Voici quelques chiffres à retenir. Le système produit environ deux virgule trois mégabits par seconde. Une coupure de deux minutes représente trente-cinq mégaoctets de données en attente. Avec un débit de cinq mégabits par seconde, le rattrapage dure à peu près cent secondes.
</p>

<p align="justify">
    Pour réaliser ce projet, nous utilisons plusieurs outils : <b> Docker </b> pour isoler les programmes, <b> Ansible </b> pour installer les machines automatiquement, <b> Prometheus </b> et <b> Grafana </b> pour les mesures, et <b> Whisper </b> pour la transcription. Le professeur ralentira la connexion avec une commande appelée <b>tc</b>, puis observera comment le système se rattrape. Le jour de la démonstration, <i> tout doit redémarrer en quelques minutes</i>.
</p>

<p align="justify">
    Enfin, il faut mesurer tout cela avec précision. On relève la <i> latence </i>, la <i> mémoire utilisée </i>, le <i> processeur </i> et l'<i> énergie consommée </i>. Un <i> tableau de bord </i> permet de voir en direct ce qui se passe, même pendant une panne. Une fonctionnalité qui n'est pas mesurée ne prouve rien.
</p>

<p align="justify">
    Cette démarche est utile en Afrique, où la connexion est parfois irrégulière. Un hôpital à Garoua, une école à Bertoua ou une station de radio à Buea pourraient en profiter. Le traitement local réduit les coûts et protège les données.
</p>

<p align="justify">
    Now we will switch to English. The edge machine analyzes the video locally and sends only the useful results to the cloud. If the network connection drops for two minutes, the system keeps everything in a buffer and sends it later. Latency, memory, and energy are measured at every step. Yaoundé and Douala are two major cities in Cameroon. The goal is simple: save bandwidth, stay reliable, and prove it with numbers.

    Merci de votre attention/Thank you for listening. 
</p>

> Fin du script.